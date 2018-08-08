DROP TABLE IF EXISTS public.temporary_restock_recipient_lookup;
DROP MATERIALIZED VIEW IF EXISTS public.temporary_transaction_recipients_view;

--------------------------------------------------------------------------------
-- Step 1, Create temporary table and materialized view
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 1: Creating temporary table and materialized view'; END $$;
CREATE MATERIALIZED VIEW public.temporary_transaction_recipients_view AS (
  SELECT
    COALESCE(fpds.awardee_or_recipient_uniqu, fabs.awardee_or_recipient_uniqu) AS awardee_or_recipient_uniqu,
    UPPER(COALESCE(fpds.ultimate_parent_legal_enti, fabs.ultimate_parent_legal_enti)) AS ultimate_parent_legal_enti,
    COALESCE(fpds.ultimate_parent_unique_ide, fabs.ultimate_parent_unique_ide) AS ultimate_parent_unique_ide,
    UPPER(COALESCE(fpds.awardee_or_recipient_legal, fabs.awardee_or_recipient_legal)) AS awardee_or_recipient_legal,
    COALESCE(fpds.legal_entity_city_name, fabs.legal_entity_city_name) AS city,
    COALESCE(fpds.legal_entity_state_code, fabs.legal_entity_state_code) AS state,
    COALESCE(fpds.legal_entity_zip5, fabs.legal_entity_zip5) AS zip5,
    COALESCE(fpds.legal_entity_zip_last4, fabs.legal_entity_zip_last4) AS zip4,
    COALESCE(fpds.legal_entity_congressional, fabs.legal_entity_congressional) AS congressional,
    COALESCE(fpds.legal_entity_address_line1, fabs.legal_entity_address_line1) AS address_line1,
    COALESCE(fpds.legal_entity_address_line2, fabs.legal_entity_address_line1) AS address_line2,
    COALESCE(fpds.legal_entity_country_code, fabs.legal_entity_country_code) AS country_code,
    tn.action_date
  FROM
    transaction_normalized AS tn
  LEFT OUTER JOIN transaction_fpds AS fpds ON
    (tn.id = fpds.transaction_id AND tn.is_fpds = TRUE)
  LEFT OUTER JOIN transaction_fabs AS fabs ON
    (tn.id = fabs.transaction_id AND tn.is_fpds = FALSE)
);

VACUUM ANALYZE public.temporary_transaction_recipients_view;


CREATE TABLE public.temporary_restock_recipient_lookup (
    recipient_hash uuid,
    legal_business_name text,
    duns text,
    parent_duns text,
    parent_legal_business_name text,
    address_line_1 text,
    address_line_2 text,
    city text,
    state text,
    zip5 text,
    zip4 text,
    country_code text,
    congressional_district text,
    business_types_codes text[]
);

CREATE UNIQUE INDEX idx_temporary_restock_recipient_lookup_unique_duns ON public.temporary_restock_recipient_lookup (duns);


--------------------------------------------------------------------------------
-- Step 2a, Create rows with Parent DUNS + Parent Recipient Names from SAM
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 2a: Creating records from SAM parent data'; END $$;
WITH grouped_parent_recipients AS (
    SELECT
    DISTINCT ON (ultimate_parent_unique_ide, ultimate_parent_legal_enti)
      ultimate_parent_unique_ide AS duns,
      ultimate_parent_legal_enti AS legal_business_name
    FROM duns
    WHERE ultimate_parent_unique_ide IS NOT NULL AND ultimate_parent_legal_enti IS NOT NULL
    ORDER BY ultimate_parent_unique_ide, ultimate_parent_legal_enti, broker_duns_id DESC
)
INSERT INTO public.temporary_restock_recipient_lookup (
    recipient_hash, legal_business_name, duns, parent_duns, parent_legal_business_name)
SELECT
    MD5(UPPER(CONCAT(gpr.duns, gpr.legal_business_name)))::uuid AS recipient_hash,
    UPPER(gpr.legal_business_name) AS legal_business_name,
    gpr.duns AS duns,
    gpr.duns AS parent_duns,
    UPPER(gpr.legal_business_name) AS parent_legal_business_name
FROM grouped_parent_recipients AS gpr
ON CONFLICT (duns) DO NOTHING;


--------------------------------------------------------------------------------
-- Step 2b, Upsert rows with DUNS + Recipient Names from SAM
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 2b: Adding/updating records from SAM'; END $$;

INSERT INTO public.temporary_restock_recipient_lookup (
  recipient_hash, legal_business_name, duns,
  parent_duns, parent_legal_business_name, address_line_1,
  address_line_2, city, state, zip5, zip4, country_code,
  congressional_district, business_types_codes
  )
  SELECT
    DISTINCT ON (awardee_or_recipient_uniqu, legal_business_name)
    MD5(UPPER(CONCAT(awardee_or_recipient_uniqu, legal_business_name)))::uuid AS recipient_hash,
    UPPER(legal_business_name) AS legal_business_name,
    awardee_or_recipient_uniqu AS duns,
    ultimate_parent_unique_ide AS parent_duns,
    UPPER(ultimate_parent_legal_enti) AS parent_legal_business_name,
    address_line_1,
    address_line_2,
    city,
    state,
    zip as zip5,
    zip4,
    country_code,
    congressional_district,
    business_types_codes
  FROM duns
  ORDER BY awardee_or_recipient_uniqu, legal_business_name, update_date DESC
ON CONFLICT (duns) DO UPDATE SET
    parent_legal_business_name = excluded.parent_legal_business_name,
    address_line_1 = excluded.address_line_1,
    address_line_2 = excluded.address_line_2,
    city = excluded.city,
    state = excluded.state,
    zip5 = excluded.zip5,
    zip4 = excluded.zip4,
    country_code = excluded.country_code,
    congressional_district = excluded.congressional_district,
    business_types_codes = excluded.business_types_codes;

VACUUM ANALYZE public.temporary_restock_recipient_lookup;


--------------------------------------------------------------------------------
-- Step 3a, Create rows with data from FPDS/FABS
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 3a: Adding missing DUNS records from FPDS and FABS'; END $$;
WITH transaction_recipients AS (
    WITH transaction_recipients_inner AS (
      SELECT
        tf.awardee_or_recipient_uniqu,
        tf.ultimate_parent_legal_enti,
        tf.ultimate_parent_unique_ide,
        tf.awardee_or_recipient_legal,
        tf.city,
        tf.state,
        tf.zip5,
        tf.zip4,
        tf.congressional,
        tf.address_line1,
        tf.address_line2,
        tf.country_code
      FROM public.temporary_transaction_recipients_view AS tf
      WHERE tf.awardee_or_recipient_uniqu IS NOT NULL
      ORDER BY tf.action_date DESC
    )
    SELECT
      DISTINCT awardee_or_recipient_uniqu,
      MD5(UPPER(CONCAT(awardee_or_recipient_uniqu, awardee_or_recipient_legal)))::uuid AS recipient_hash,
      awardee_or_recipient_uniqu AS duns,
      ultimate_parent_unique_ide AS parent_duns,
      ultimate_parent_legal_enti AS parent_legal_business_name,
      awardee_or_recipient_legal AS legal_business_name,
      city,
      state,
      zip5,
      zip4,
      congressional AS congressional_district,
      address_line1 AS address_line_1,
      address_line2 AS address_line_2,
      country_code
    FROM transaction_recipients_inner
)

INSERT INTO public.temporary_restock_recipient_lookup (
    recipient_hash, legal_business_name, duns, parent_duns,
    parent_legal_business_name, address_line_1, address_line_2, city,
     state, zip5, zip4, country_code,
    congressional_district)
SELECT
    recipient_hash, legal_business_name, duns, parent_duns,
    parent_legal_business_name, address_line_1, address_line_2, city,
    state, zip5, zip4, country_code,
    congressional_district
FROM transaction_recipients
ON CONFLICT (duns) DO NOTHING;


--------------------------------------------------------------------------------
-- Step 3b, Create rows with Parent DUNS + Parent Recipient Names from FPDS/FABS
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 3b: Adding missing DUNS records from FPDS and FABS (parents)'; END $$;
WITH transaction_recipients AS (
    WITH transaction_recipients_inner AS (
      SELECT
        tf.ultimate_parent_legal_enti,
        tf.ultimate_parent_unique_ide
      FROM public.temporary_transaction_recipients_view AS tf
      WHERE tf.ultimate_parent_unique_ide IS NOT NULL AND tf.ultimate_parent_legal_enti IS NOT NULL
      ORDER BY tf.action_date DESC
    )
    SELECT
      DISTINCT ultimate_parent_unique_ide,
      MD5(UPPER(CONCAT(ultimate_parent_unique_ide, ultimate_parent_legal_enti)))::uuid AS recipient_hash,
      ultimate_parent_unique_ide AS parent_duns,
      ultimate_parent_legal_enti AS parent_legal_business_name,
      ultimate_parent_unique_ide AS duns,
      ultimate_parent_legal_enti AS legal_business_name
    FROM transaction_recipients_inner
)

INSERT INTO public.temporary_restock_recipient_lookup (
    recipient_hash, legal_business_name, duns, parent_duns,
    parent_legal_business_name)
SELECT
    recipient_hash, legal_business_name, duns, parent_duns,
    parent_legal_business_name
FROM transaction_recipients
ON CONFLICT (duns) DO NOTHING;

DROP INDEX idx_temporary_restock_recipient_lookup_unique_duns;
CREATE UNIQUE INDEX idx_temporary_restock_recipient_lookup_hash ON public.temporary_restock_recipient_lookup (recipient_hash);


--------------------------------------------------------------------------------
-- Step 4, Adding duns-less records from FPDS and FABS
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 4: Adding duns-less records from FPDS and FABS'; END $$;

WITH transaction_recipients AS (
    WITH transaction_recipients_inner AS (
      SELECT
        tf.awardee_or_recipient_uniqu,
        tf.ultimate_parent_legal_enti,
        tf.ultimate_parent_unique_ide,
        tf.awardee_or_recipient_legal,
        tf.city,
        tf.state,
        tf.zip5,
        tf.zip4,
        tf.congressional,
        tf.address_line1,
        tf.address_line2,
        tf.country_code
      FROM public.temporary_transaction_recipients_view AS tf
      WHERE tf.awardee_or_recipient_uniqu IS NULL
      ORDER BY tf.action_date DESC
  )
    SELECT
      DISTINCT awardee_or_recipient_legal,
      MD5(UPPER(CONCAT(awardee_or_recipient_uniqu, awardee_or_recipient_legal)))::uuid AS recipient_hash,
      awardee_or_recipient_uniqu AS duns,
      ultimate_parent_legal_enti AS parent_duns,
      ultimate_parent_unique_ide AS parent_legal_business_name,
      awardee_or_recipient_legal AS legal_business_name,
      city,
      state,
      zip5,
      zip4,
      congressional AS congressional_district,
      address_line1 AS address_line_1,
      address_line2 AS address_line_2,
      country_code
    FROM transaction_recipients_inner
)

INSERT INTO public.temporary_restock_recipient_lookup (
    recipient_hash, legal_business_name, duns, parent_duns,
    parent_legal_business_name, address_line_1, address_line_2, city,
     state, zip5, zip4, country_code,
    congressional_district)
SELECT
    MD5(UPPER(CONCAT(duns, legal_business_name)))::uuid AS recipient_hash,
    legal_business_name, duns, parent_duns,
    parent_legal_business_name, address_line_1, address_line_2, city,
    state, zip5, zip4, country_code,
    congressional_district
FROM transaction_recipients
ON CONFLICT (recipient_hash) DO NOTHING;


--------------------------------------------------------------------------------
-- Step 5, Finalizing
--------------------------------------------------------------------------------
DO $$ BEGIN RAISE NOTICE 'Step 5: restocking destination table'; END $$;
BEGIN;
TRUNCATE TABLE public.recipient_lookup RESTART IDENTITY;
INSERT INTO public.recipient_lookup (
    recipient_hash, legal_business_name, duns, address_line_1, address_line_2, city,
     state, zip5, zip4, country_code,
    congressional_district, business_types_codes)
  SELECT
    recipient_hash,
    legal_business_name,
    duns,
    address_line_1,
    address_line_2,
    city,
    state,
    zip5,
    zip4,
    country_code,
    congressional_district,
    business_types_codes
 FROM public.temporary_restock_recipient_lookup;
DROP TABLE public.temporary_restock_recipient_lookup;
DROP MATERIALIZED VIEW IF EXISTS public.temporary_transaction_recipients_view;
COMMIT;

VACUUM ANALYZE public.recipient_lookup;

----------------------WORKING FOR TIER 1-------------------------------------


-- Dimension table: one row per standardized district
CREATE TABLE dim_district (
    district_id     INT PRIMARY KEY,
    district_name   TEXT NOT NULL
	state_name      TEXT
);


-- Raw health table
CREATE TABLE raw_health (
    district_id                   INT REFERENCES dim_district(district_id),
    state_name                    TEXT,
    institutional_births_pct      NUMERIC,
    full_immunization_pct         NUMERIC,
    stunted_pct                   NUMERIC,
    wasted_pct                    NUMERIC,
    underweight_pct               NUMERIC,
    child_anaemia_pct             NUMERIC,
    pregnant_women_anaemia_pct    NUMERIC,
    diarrhoea_prevalence_pct      NUMERIC,
    ari_prevalence_pct            NUMERIC,
    antenatal_care_4visits_pct    NUMERIC,
    postnatal_care_pct            NUMERIC,
    household_electricity_pct     NUMERIC,
    household_drinking_water_pct  NUMERIC,
    household_sanitation_pct      NUMERIC,
    health_insurance_pct          NUMERIC,
    womens_literacy_health_survey NUMERIC
);

-- Raw education table
CREATE TABLE raw_education (
    district_id                        INT REFERENCES dim_district(district_id),
    state_name                         TEXT,
    overall_literacy                   NUMERIC,
    female_literacy                    NUMERIC,
    male_literacy                      NUMERIC,
    total_enrollment                   INT,
    govt_enrollment                    INT,
    private_enrollment                 INT,
    school_age_population              INT,
    primary_pupil_teacher_ratio        NUMERIC,
    upper_primary_pupil_teacher_ratio  NUMERIC,
    total_schools                      INT,
    schools_with_water                 INT,
    schools_with_electricity           INT,
    schools_with_girls_toilet          INT,
    schools_with_boys_toilet           INT,
    schools_with_road_connectivity     INT,
    pct_sc_population                  NUMERIC,
    pct_st_population                  NUMERIC,
    dropout_rate_pct                   NUMERIC,
    pct_govt_enrollment                NUMERIC,
    pct_private_enrollment             NUMERIC,
    pct_schools_road_connected         NUMERIC,
    pct_schools_electricity            NUMERIC,
    pct_schools_water                  NUMERIC,
    pct_schools_girls_toilet           NUMERIC,
    girl_dropout_rate                  NUMERIC,
    boy_dropout_rate                   NUMERIC,
    dropout_gender_gap                 NUMERIC,
    literacy_gender_gap                NUMERIC,
    toilet_gender_gap                  INT
);

--Confirm the tables were created
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

SELECT COUNT(*) FROM dim_district;
SELECT COUNT(*) FROM raw_health;
SELECT COUNT(*) FROM raw_education;

-- Check 1: no duplicate districts
SELECT district_name, state_name, COUNT(*)
FROM dim_district
GROUP BY district_name, state_name
HAVING COUNT(*) > 1;
-- should return 0 rows

-- Check 2: values out of plausible range (percentages should be 0-100)
SELECT district_id, overall_literacy
FROM raw_education
WHERE overall_literacy NOT BETWEEN 0 AND 100;
-- should return 0 rows

-- Check 3: how many districts have both health AND education data
SELECT COUNT(*)
FROM dim_district d
JOIN raw_health h ON d.district_id = h.district_id
JOIN raw_education e ON d.district_id = e.district_id;

--core join query.This is main SQL deliverable — the query that actually combines health and education data per district:
CREATE VIEW silver_district_combined AS
SELECT
    d.district_id, d.district_name, d.state_name,
    h.institutional_births_pct, h.full_immunization_pct, h.stunted_pct, h.wasted_pct,
    h.underweight_pct, h.child_anaemia_pct, h.household_electricity_pct,
    h.household_sanitation_pct, h.health_insurance_pct,
    e.overall_literacy, e.female_literacy, e.dropout_rate_pct, e.pct_govt_enrollment,
    e.pct_schools_electricity, e.pct_schools_water,
    e.literacy_gender_gap, e.dropout_gender_gap
FROM dim_district d
JOIN raw_health h ON d.district_id = h.district_id
JOIN raw_education e ON d.district_id = e.district_id;

-- ALTER TABLE raw_education DROP COLUMN primary_pupil_teacher_ratio;
ALTER TABLE raw_education ADD COLUMN total_teachers INT;

DELETE FROM raw_education;

SELECT COUNT(*) FROM raw_education;


----------------------WORKING FOR TIER 2-------------------------------------


CREATE TABLE raw_education_detail (
    district_id                  INT REFERENCES dim_district(district_id),
    repeater_rate_pct            NUMERIC,
    trained_teachers_total       INT,
    total_teachers                INT,
    schools_with_playground      INT,
    schools_with_boundary_wall   INT,
    schools_with_computer        INT
);

CREATE TABLE raw_health_detail (
    district_id                INT REFERENCES dim_district(district_id),
    vaccine_bcg_pct            NUMERIC,
    vaccine_polio_pct          NUMERIC,
    vaccine_dpt_pct            NUMERIC,
    vaccine_measles_pct        NUMERIC,
    vaccine_rotavirus_pct      NUMERIC,
    vaccine_hepatitis_b_pct    NUMERIC
);


SELECT COUNT(*) FROM raw_education_detail;  -- expect 603
SELECT COUNT(*) FROM raw_health_detail;     -- expect 706


-- Check 1: row counts match what was loaded
SELECT COUNT(*) FROM raw_education_detail;  -- expect 603
SELECT COUNT(*) FROM raw_health_detail;     -- expect 706

-- Check 2: range checks on the new percentage columns
SELECT district_id, repeater_rate_pct FROM raw_education_detail
WHERE repeater_rate_pct NOT BETWEEN 0 AND 100;

SELECT district_id, vaccine_bcg_pct FROM raw_health_detail
WHERE vaccine_bcg_pct NOT BETWEEN 0 AND 100;
-- (repeat for the other 4 vaccine columns)

-- Check 3: confirm every district_id here actually exists in dim_district (FK sanity)
SELECT COUNT(*) FROM raw_education_detail e
LEFT JOIN dim_district d ON e.district_id = d.district_id
WHERE d.district_id IS NULL;
-- should return 0

-- Check 4: a quick join preview — do Tier 1 and Tier 2 line up correctly for the same district?
SELECT d.district_name, e.dropout_rate_pct, ed.repeater_rate_pct
FROM dim_district d
JOIN raw_education e ON d.district_id = e.district_id
JOIN raw_education_detail ed ON d.district_id = ed.district_id
LIMIT 10;
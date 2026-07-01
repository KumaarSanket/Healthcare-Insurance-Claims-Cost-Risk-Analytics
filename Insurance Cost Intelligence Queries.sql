CREATE DATABASE IF NOT EXISTS insurance_project;
USE insurance_project;

DROP TABLE IF EXISTS insurance_claims;

CREATE TABLE insurance_claims (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    age         TINYINT,
    sex         VARCHAR(10),
    bmi         DECIMAL(5,2),
    children    TINYINT,
    smoker      TINYINT(1),
    region      VARCHAR(15),
    charges     DECIMAL(10,2)
);

USE insurance_project;
SET SESSION sql_mode = '';

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/insurance_cleaned.csv'
INTO TABLE insurance_claims
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(age, sex, bmi, children, @smoker_raw, region, charges)
SET smoker = IF(TRIM(@smoker_raw) = 'yes', 1, 0);

SELECT COUNT(*) FROM insurance_claims;
-- Should show: 1,337 ✅

SELECT smoker, COUNT(*) FROM insurance_claims GROUP BY smoker;
-- Should show: 0 = 1063, 1 = 274 ✅

SELECT * FROM insurance_claims LIMIT 5;

CREATE INDEX idx_smoker   ON insurance_claims(smoker);
CREATE INDEX idx_region   ON insurance_claims(region);
CREATE INDEX idx_sex      ON insurance_claims(sex);
CREATE INDEX idx_age      ON insurance_claims(age);
CREATE INDEX idx_bmi      ON insurance_claims(bmi);
CREATE INDEX idx_charges  ON insurance_claims(charges);
CREATE INDEX idx_children ON insurance_claims(children);

-- Query 1 — Overall KPIs:
SELECT
    COUNT(*)                                          AS total_patients,
    ROUND(AVG(charges), 2)                            AS avg_charges,
    ROUND(MIN(charges), 2)                            AS min_charges,
    ROUND(MAX(charges), 2)                            AS max_charges,
    ROUND(AVG(age), 1)                                AS avg_age,
    ROUND(AVG(bmi), 2)                                AS avg_bmi,
    ROUND(AVG(children), 2)                           AS avg_children,
    SUM(smoker)                                       AS total_smokers,
    ROUND(SUM(smoker)*100.0/COUNT(*), 2)             AS smoker_pct,
    COUNT(*) - SUM(smoker)                           AS total_non_smokers
FROM insurance_claims;

-- Query 2 — Smoker vs Non-Smoker Cost Comparison
SELECT
    CASE WHEN smoker = 1 THEN 'Smoker' ELSE 'Non-Smoker' END  AS smoker_status,
    COUNT(*)                                                    AS total_patients,
    ROUND(AVG(charges), 2)                                     AS avg_charges,
    ROUND(MIN(charges), 2)                                     AS min_charges,
    ROUND(MAX(charges), 2)                                     AS max_charges,
    ROUND(AVG(bmi), 2)                                         AS avg_bmi,
    ROUND(AVG(age), 1)                                         AS avg_age
FROM insurance_claims
GROUP BY smoker
ORDER BY avg_charges DESC;

-- Query 3 — Average Charges by Region
SELECT
    region,
    COUNT(*)                                          AS total_patients,
    ROUND(AVG(charges), 2)                            AS avg_charges,
    SUM(smoker)                                       AS smokers_in_region,
    ROUND(SUM(smoker)*100.0/COUNT(*), 2)             AS smoker_pct,
    ROUND(AVG(bmi), 2)                                AS avg_bmi
FROM insurance_claims
GROUP BY region
ORDER BY avg_charges DESC;

-- Query 4 — Charges by Age Group
SELECT
    CASE
        WHEN age BETWEEN 18 AND 24 THEN '01 — 18 to 24'
        WHEN age BETWEEN 25 AND 34 THEN '02 — 25 to 34'
        WHEN age BETWEEN 35 AND 44 THEN '03 — 35 to 44'
        WHEN age BETWEEN 45 AND 54 THEN '04 — 45 to 54'
        ELSE                             '05 — 55 to 64'
    END                                               AS age_group,
    COUNT(*)                                          AS total_patients,
    ROUND(AVG(charges), 2)                            AS avg_charges,
    SUM(smoker)                                       AS smokers,
    ROUND(AVG(bmi), 2)                                AS avg_bmi
FROM insurance_claims
GROUP BY age_group
ORDER BY age_group;

-- Query 5 — BMI Group vs Charges
SELECT
    CASE
        WHEN bmi < 18.5              THEN '01 — Underweight (<18.5)'
        WHEN bmi BETWEEN 18.5 AND 24.99 THEN '02 — Normal (18.5-25)'
        WHEN bmi BETWEEN 25 AND 29.99   THEN '03 — Overweight (25-30)'
        WHEN bmi BETWEEN 30 AND 34.99   THEN '04 — Obese (30-35)'
        ELSE                              '05 — Severely Obese (35+)'
    END                                               AS bmi_group,
    COUNT(*)                                          AS total_patients,
    ROUND(AVG(charges), 2)                            AS avg_charges,
    SUM(smoker)                                       AS smokers,
    ROUND(SUM(smoker)*100.0/COUNT(*), 2)             AS smoker_pct
FROM insurance_claims
GROUP BY bmi_group
ORDER BY bmi_group;

-- Query 6 — Risk Level Segmentation
SELECT
    CASE
        WHEN charges < 5000              THEN '01 — Low Risk (Under $5K)'
        WHEN charges BETWEEN 5000 AND 14999 THEN '02 — Medium Risk ($5K-$15K)'
        ELSE                                  '03 — High Risk (Over $15K)'
    END                                               AS risk_level,
    COUNT(*)                                          AS total_patients,
    ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM insurance_claims), 2) AS pct_of_total,
    ROUND(AVG(charges), 2)                            AS avg_charges,
    SUM(smoker)                                       AS smokers,
    ROUND(SUM(smoker)*100.0/COUNT(*), 2)             AS smoker_pct,
    ROUND(AVG(age), 1)                                AS avg_age,
    ROUND(AVG(bmi), 2)                                AS avg_bmi
FROM insurance_claims
GROUP BY risk_level
ORDER BY risk_level;

-- Query 7 — Smoker × BMI Group Combination
SELECT
    CASE WHEN smoker = 1 THEN 'Smoker' ELSE 'Non-Smoker' END AS smoker_status,
    CASE
        WHEN bmi < 18.5                  THEN '01 — Underweight'
        WHEN bmi BETWEEN 18.5 AND 24.99  THEN '02 — Normal'
        WHEN bmi BETWEEN 25 AND 29.99    THEN '03 — Overweight'
        WHEN bmi BETWEEN 30 AND 34.99    THEN '04 — Obese'
        ELSE                                  '05 — Severely Obese'
    END                                                       AS bmi_group,
    COUNT(*)                                                  AS total_patients,
    ROUND(AVG(charges), 2)                                    AS avg_charges,
    ROUND(MIN(charges), 2)                                    AS min_charges,
    ROUND(MAX(charges), 2)                                    AS max_charges
FROM insurance_claims
GROUP BY smoker_status, bmi_group
ORDER BY smoker_status, bmi_group;

-- Query 8 — Create Analytical VIEW
CREATE OR REPLACE VIEW vw_insurance_summary AS
SELECT
    CASE WHEN smoker = 1 THEN 'Smoker' ELSE 'Non-Smoker' END AS smoker_status,
    sex,
    region,
    CASE
        WHEN age BETWEEN 18 AND 24 THEN '01-18 to 24'
        WHEN age BETWEEN 25 AND 34 THEN '02-25 to 34'
        WHEN age BETWEEN 35 AND 44 THEN '03-35 to 44'
        WHEN age BETWEEN 45 AND 54 THEN '04-45 to 54'
        ELSE                             '05-55 to 64'
    END                                                       AS age_group,
    CASE
        WHEN bmi < 18.5                  THEN '01-Underweight'
        WHEN bmi BETWEEN 18.5 AND 24.99  THEN '02-Normal'
        WHEN bmi BETWEEN 25 AND 29.99    THEN '03-Overweight'
        WHEN bmi BETWEEN 30 AND 34.99    THEN '04-Obese'
        ELSE                                  '05-Severely Obese'
    END                                                       AS bmi_group,
    CASE
        WHEN charges < 5000              THEN '01-Low Risk'
        WHEN charges BETWEEN 5000 AND 14999 THEN '02-Medium Risk'
        ELSE                                  '03-High Risk'
    END                                                       AS risk_level,
    CASE
        WHEN charges < 5000                  THEN '01-Under 5K'
        WHEN charges BETWEEN 5000 AND 9999   THEN '02-5K-10K'
        WHEN charges BETWEEN 10000 AND 19999 THEN '03-10K-20K'
        WHEN charges BETWEEN 20000 AND 34999 THEN '04-20K-35K'
        ELSE                                      '05-35K+'
    END                                                       AS charges_bucket,
    CASE
        WHEN children = 0  THEN 'No Children'
        WHEN children <= 2 THEN '1-2 Children'
        ELSE                    '3+ Children'
    END                                                       AS children_group,
    COUNT(*)                                                  AS total_patients,
    ROUND(AVG(charges), 2)                                    AS avg_charges,
    ROUND(MIN(charges), 2)                                    AS min_charges,
    ROUND(MAX(charges), 2)                                    AS max_charges,
    ROUND(AVG(bmi), 2)                                        AS avg_bmi,
    ROUND(AVG(age), 1)                                        AS avg_age
FROM insurance_claims
GROUP BY smoker_status, sex, region, age_group, bmi_group, risk_level, charges_bucket, children_group;
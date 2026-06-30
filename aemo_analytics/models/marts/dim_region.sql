{{ config(
    materialized='table',
    schema='MARTS'
) }}

SELECT * FROM (
    VALUES
        ('NSW1', 'New South Wales',     'Australia/Sydney'),
        ('VIC1', 'Victoria',            'Australia/Melbourne'),
        ('QLD1', 'Queensland',          'Australia/Brisbane'),
        ('SA1',  'South Australia',     'Australia/Adelaide'),
        ('TAS1', 'Tasmania',            'Australia/Hobart')
) AS t (region_code, region_name, timezone)
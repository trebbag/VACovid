# VACovid

[![VACovid-automater-gg](https://github.com/trebbag/VACovid/actions/workflows/automater.yml/badge.svg)](https://github.com/trebbag/VACovid/actions/workflows/automater.yml)

## Introduction

This project first started at the beginning of the COVID-19 pandemic. The VA's Office of Electronic Health Record Modernization (OEHRM) has a mission to implement a new EHR system across the United States. However, implementation at each site is a complex task and a large task for each hospital. With the pandemic, OEHRM staff needed to be sensitive to the extra burden that COVID-19 was placing on each facility, particularly the sites that were next on schedule for implementation. 

## Data Sources / Methodology

This data project starts with the daily case counts by county uploaded by the NYTimes.

### Veteran Cases per County
Utilizing veteran population data by county and census population data by county, the proportion of each county's population that is made up of Veterans could be established. This is directly applied to the case count totals to get an estimate of veteran cases per county. This process is probabilistic and assumes that there are no confounding variables that would serve to confer additional protection/risk to veterans compared to the general public. 

### Veteran Hospitalizations
The more difficult aspect of this project was establishing estimates of hospitalization. To start, publicly available CDC data of over 30 million cases was used to estimate the age distribution of cases per county (i.e., what percentage of cases in X County occured in 17-44 year olds). These percentages were then applied to the NYTimes daily cases to get an estimated breakdown of each county's cases by age group.

Next, veteran population data by age and census population data by age for each county was used to break the total cases into estimated veteran cases (as was down for Veteran Cases per County). 

Finally, data analytics were collected for the general risk of hospitalization per case by age group. These percentages are shown below. Each risk percentage was applied to the respective age group case count to get estimated hospitalized cases by age group. The sum of these cases was used to reach the general estimated number of hospitalizations given the number of cases.

* Age 17-44:  0.6% - 5.1%
* Age 45-64:  5.45% - 14.8%
* Age 65-84:  15.9% - 26.25%
* Age 85+:    26.25% - 45%  

## Repository Files

The following is a brief orientation of the files in the respository:
* Population.py - runs the basic population proportion measurements. Only needs to be run when new census or veteran data is used.
* CaseInsert.py - original file for daily case data transformations to output for data visualizations
* CCTPull.py - defined function for case data transformations for OEHRM leadership needs
* CountyVACOVID.csv - output of all veteran based transformations of daily COVID data - all other outputs are assorted geographic filters from this file 
* VAChart.csv - orginal data visualization output needs
* CCTVAChart2.csv - data output needs for OEHRM leadership - Version 2

Data preparation and analytics by Greg Gabbert, MD MPH

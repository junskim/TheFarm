- Capstone Project for [Galvanize](http://www.galvanize.com/) Data Science Immersive - Seattle Cohort 4.
- Jun Soo Kim ([LinkedIn](https://www.linkedin.com/in/jun-soo-kim)).

# The Farm: Who Gets Harvested?

## Motivation

It is every Minor League Baseball player's dream to play in the Major League Baseball (MLB). One main reason can be from a significant difference in the salary. [While the minimum salary is $2,150 per month for an AAA player](http://www.sportslawblogger.com/baseball/salary-information/minor-league-salary/), the minimum salary of the MLB [is reported as $507,500](http://www.baseball-reference.com/bullpen/Minimum_salary). Plus, MLB players [earn a pension after just 43 days in the Majors](http://www.businessinsider.com/nfl-nhl-nba-mlb-retirement-pension-plans-lockout-2011-1).
![Salary](https://github.com/danhwangya/TheFarm/blob/master/Images/salary.png)

It was for my best interest to predict a player's chance of making it to the Majors next year given yearly stats.

## Overview

![Overall Picture](https://github.com/danhwangya/TheFarm/blob/master/Images/Flow.png)

## Data
I scrapped most of my data from [Baseball-Reference](http://www.baseball-reference.com/).

I used Minor League Baseball players data from 2000 to 2016, as I was more interested in recent "trend" of scouting. Here are few things that I did with the data:

1. Excluded players who never played in the United States.

2. Extracted list of players who appeared in the MLB for the first time each year. I used the list to label the data in later steps with make/not make to the majors. For example, if a player first appeared in 2013, then the player's stats in 2012 is labeled with a positive class, with removing any data after 2012, since what I care is FIRST appearance of the player in the MLB.

3. Divided the players into two categories: Pitchers and Batters (or Positional Players) using the position info from each player's bio section.

Data was quite imbalanced, with only 1% positive class. ![imbalanced_class](https://github.com/danhwangya/TheFarm/blob/master/Images/Imbalanced.jpg)

## Modeling & Evaluation
I tried to model two different models: one for the pitchers and one for the positional players. I used three models: Logistic Regression, Random Forest Classifier, and Gradient Boost Classifier. Logistic Regression had the best result, however Random Forest's result was very close to that of Logistic Regression.

**1. Original Data**

| Will make it<br>to the majors<br>next year?   | Predicted<br>**Yes** | Predicted<br>**No** |
| :---: | :---: | :---: |
|**Actual**<br>**Yes**| **0**<br>0.00%<br>(True Positive)     | **145**<br>1.00%<br>(False Negative) |
|**Actual**<br>**No**| **0**<br>0.00%<br>(False Positive)     | **13383**<br>99.0%<br>(True Negative) |

**2. After random undersampling (0.5)**

| Will make it<br>to the majors<br>next year?   | Predicted<br>**Yes** | Predicted<br>**No** |
| :---: | :---: | :---: |
|**Actual**<br>**Yes**| **114**<br>0.80%<br>(True Positive)     | **31**<br>0.20%<br>(False Negative) |
|**Actual**<br>**No**| **1900**<br>14.0%<br>(False Positive)     | **11483**<br>85.0%<br>(True Negative) |

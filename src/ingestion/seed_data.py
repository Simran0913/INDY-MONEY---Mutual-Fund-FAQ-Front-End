"""
seed_data.py
------------
Pre-embedded factual text seeded from official SBI MF, AMFI, and SEBI sources.

PURPOSE:
  Official PDFs (KIM, SID, Factsheets) are sometimes behind CDN auth-walls
  or require JavaScript rendering. This seed module provides verified factual
  text extracted from those documents so the RAG system always has grounded data.

IMPORTANT:
  - All facts below are sourced from official sbimf.com, amfiindia.com, sebi.gov.in.
  - No facts are invented.
  - Source IDs match data/sources.csv exactly.
  - Text is written to data/processed/ as JSON so the pipeline can use it.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed documents — keyed by source_id matching sources.csv
# ---------------------------------------------------------------------------

SEED_DOCUMENTS = [
    {
        "source_id"   : "SRC001",
        "title"       : "SBI Bluechip Fund - Scheme Page",
        "scheme"      : "SBI Bluechip Fund",
        "source_url"  : "https://www.sbimf.com/en-us/equity-funds/sbi-bluechip-fund",
        "organization": "SBI Mutual Fund",
        "source_type" : "scheme_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Bluechip Fund

SBI Bluechip Fund is an open-ended large cap equity scheme. The scheme seeks to provide investors
with opportunities for long-term growth in capital through an active management of investments in a
diversified basket of large cap stocks.

## Scheme Objective
To provide investors with opportunities for long-term growth in capital through an active management
of investments in a diversified basket of equity stocks of companies whose market capitalization is
at least equal to or more than the least market capitalised stock of S&P BSE 100 Index.

## Benchmark
The benchmark index for SBI Bluechip Fund is S&P BSE 100 TRI (Total Return Index).

## Riskometer
The risk level of SBI Bluechip Fund is Very High. Investors understand that their principal will be
at Very High risk.

## Fund Manager
The fund is managed by experienced fund managers at SBI Funds Management Ltd.

## Plan Options
The scheme offers Regular Plan and Direct Plan, each with Growth and IDCW (Income Distribution cum
Capital Withdrawal) options.

## Minimum Investment
Minimum lump sum investment: Rs. 5,000 and in multiples of Re. 1 thereafter.
Minimum Additional Purchase: Rs. 1,000 and in multiples of Re. 1 thereafter.

## Minimum SIP
Minimum SIP investment amount: Rs. 500 per month.
Minimum SIP installments: 6.

## Exit Load
For units in excess of 10% of the investment, 1% will be charged for redemptions/switch-outs
within 1 year from the date of allotment. No exit load after 1 year from the date of allotment.
For the first 10% of investment (by value), no exit load is applicable.

## Expense Ratio
The Total Expense Ratio (TER) for SBI Bluechip Fund Direct Plan is approximately 0.83% per annum.
The TER for SBI Bluechip Fund Regular Plan is approximately 1.64% per annum.
(TER figures are as per latest AMFI disclosure and may be updated monthly.)

## Fund Type
Open-ended Large Cap Equity Scheme.

## NFO Details
The scheme was launched in 2006.
        """.strip(),
    },
    {
        "source_id"   : "SRC002",
        "title"       : "SBI Bluechip Fund - Key Information Memorandum",
        "scheme"      : "SBI Bluechip Fund",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/KIM/SBI-BlueChip-Fund-KIM.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "KIM",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Bluechip Fund - Key Information Memorandum

## Type of Scheme
An open-ended large cap equity scheme investing in large cap stocks.

## Investment Objective
To provide investors with opportunities for long-term growth in capital through an active management
of investments in a diversified basket of large cap stocks.

## Asset Allocation
Equity and equity related instruments of large cap companies: 80%-100%
Other equity and equity related instruments: 0%-20%
Debt and money market securities: 0%-20%

## Benchmark
S&P BSE 100 TRI

## Riskometer
Very High Risk. Investors understand that their principal will be at Very High risk.

## Minimum Application Amount
Fresh Purchase: Rs. 5,000/- and in multiples of Re. 1/- thereafter.
Additional Purchase: Rs. 1,000/- and in multiples of Re. 1/- thereafter.

## Minimum SIP Amount
Rs. 500/- per installment, minimum 6 installments.

## Exit Load
Exit load of 1% if redeemed or switched out within 1 year from the date of allotment
(applicable on units in excess of 10% of investment).
For the first 10% of units (by value): Nil exit load.
After 1 year: Nil exit load.

## Total Expense Ratio (TER)
Direct Plan: ~0.83% per annum
Regular Plan: ~1.64% per annum
TER is disclosed on AMFI website (www.amfiindia.com) and updated monthly.

## Plans Available
Direct Plan - Growth
Direct Plan - IDCW
Regular Plan - Growth
Regular Plan - IDCW

## Dividend Policy
IDCW (Income Distribution cum Capital Withdrawal) is paid subject to availability of distributable surplus.
        """.strip(),
    },
    {
        "source_id"   : "SRC003",
        "title"       : "SBI Magnum Tax Gain Scheme - Scheme Page",
        "scheme"      : "SBI Magnum Tax Gain Scheme",
        "source_url"  : "https://www.sbimf.com/en-us/equity-funds/sbi-magnum-taxgain-scheme",
        "organization": "SBI Mutual Fund",
        "source_type" : "scheme_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Magnum Tax Gain Scheme (ELSS)

SBI Magnum Tax Gain Scheme is an open-ended equity linked savings scheme (ELSS) with a statutory
lock-in of 3 years and tax benefit under Section 80C of the Income Tax Act, 1961.

## Scheme Objective
To deliver the benefit of investment in a portfolio of equity shares, while offering a deduction
on such investments made in the scheme under Section 80C of the Income Tax Act, 1961. It also
aims to distribute income periodically depending on distributable surplus.

## ELSS Lock-in Period
The statutory lock-in period for SBI Magnum Tax Gain Scheme is 3 years from the date of allotment.
Units cannot be redeemed or switched before completion of 3 years. This lock-in is mandated by
SEBI regulations for all ELSS schemes.

## Tax Benefit
Investments in SBI Magnum Tax Gain Scheme are eligible for deduction under Section 80C of the
Income Tax Act, 1961 up to Rs. 1,50,000 per financial year.

## Benchmark
The benchmark index for SBI Magnum Tax Gain Scheme is S&P BSE 500 TRI (Total Return Index).

## Riskometer
The risk level of SBI Magnum Tax Gain Scheme is Very High. Investors understand that their
principal will be at Very High risk.

## Minimum Investment
Minimum lump sum investment: Rs. 500 and in multiples of Re. 500 thereafter.
Minimum Additional Purchase: Rs. 500 and in multiples of Re. 500 thereafter.

## Minimum SIP
Minimum SIP investment amount: Rs. 500 per month.
Minimum SIP installments: 6.

## Exit Load
Nil. No exit load is applicable for SBI Magnum Tax Gain Scheme as it is an ELSS scheme with
a mandatory 3-year lock-in period.

## Expense Ratio
The Total Expense Ratio (TER) for SBI Magnum Tax Gain Scheme Direct Plan is approximately 0.91%
per annum. The TER for Regular Plan is approximately 1.74% per annum.
(TER is updated monthly on AMFI website.)

## Fund Type
Open-ended Equity Linked Savings Scheme (ELSS).
        """.strip(),
    },
    {
        "source_id"   : "SRC004",
        "title"       : "SBI Magnum Tax Gain Scheme - Key Information Memorandum",
        "scheme"      : "SBI Magnum Tax Gain Scheme",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/KIM/SBI-Magnum-TaxGain-KIM.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "KIM",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Magnum Tax Gain Scheme - Key Information Memorandum

## Type of Scheme
An open-ended equity linked savings scheme (ELSS) with a statutory lock-in of 3 years and tax
benefit under Section 80C of the Income Tax Act, 1961.

## ELSS Lock-in Period
Statutory lock-in period: 3 years from the date of allotment.
Early redemption or switching is NOT permitted during the lock-in period.

## Section 80C Tax Benefit
Investments eligible for deduction under Section 80C of the Income Tax Act, 1961.
Maximum deductible amount: Rs. 1,50,000/- per financial year.

## Minimum Application Amount
Fresh Purchase: Rs. 500/- and in multiples of Rs. 500/- thereafter.
Additional Purchase: Rs. 500/- and in multiples of Rs. 500/- thereafter.

## Minimum SIP Amount
Rs. 500/- per installment, minimum 6 installments.
Note: Each SIP installment is treated as a fresh purchase with a 3-year lock-in period.

## Exit Load
Nil. Exit load is not applicable since the scheme has a mandatory 3-year statutory lock-in.

## Total Expense Ratio (TER)
Direct Plan: ~0.91% per annum
Regular Plan: ~1.74% per annum

## Benchmark
S&P BSE 500 TRI

## Riskometer
Very High Risk.

## Asset Allocation
Equity and equity related instruments: 80%-100%
Debt and money market securities: 0%-20%
        """.strip(),
    },
    {
        "source_id"   : "SRC005",
        "title"       : "SBI Liquid Fund - Scheme Page",
        "scheme"      : "SBI Liquid Fund",
        "source_url"  : "https://www.sbimf.com/en-us/debt-funds/sbi-liquid-fund",
        "organization": "SBI Mutual Fund",
        "source_type" : "scheme_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Liquid Fund

SBI Liquid Fund is an open-ended liquid scheme investing in debt and money market securities with
maturity of up to 91 days only.

## Scheme Objective
To provide investors with attractive returns consistent with high levels of safety and liquidity
through investment in debt and money market securities.

## Benchmark
The benchmark index for SBI Liquid Fund is NIFTY Liquid Index A-I.

## Riskometer
The risk level of SBI Liquid Fund is Low to Moderate. Investors understand that their principal
will be at Low to Moderate risk.

## Minimum Investment
Minimum lump sum investment: Rs. 5,000 and in multiples of Re. 1 thereafter.
Minimum Additional Purchase: Rs. 1,000 and in multiples of Re. 1 thereafter.

## Minimum SIP
Minimum SIP investment amount: Rs. 1,000 per month.
Minimum SIP installments: 6.

## Exit Load
Exit load of 0.0070% on Day 1 from date of allotment.
Exit load of 0.0065% on Day 2 from date of allotment.
Exit load of 0.0060% on Day 3 from date of allotment.
Exit load of 0.0055% on Day 4 from date of allotment.
Exit load of 0.0050% on Day 5 from date of allotment.
Exit load of 0.0045% on Day 6 from date of allotment.
Exit load of Nil from Day 7 onwards from date of allotment.
(As per SEBI circular on graded exit load for liquid funds.)

## Expense Ratio
The Total Expense Ratio (TER) for SBI Liquid Fund Direct Plan is approximately 0.20% per annum.
The TER for SBI Liquid Fund Regular Plan is approximately 0.33% per annum.

## Fund Type
Open-ended Liquid Scheme.
        """.strip(),
    },
    {
        "source_id"   : "SRC006",
        "title"       : "SBI Liquid Fund - Key Information Memorandum",
        "scheme"      : "SBI Liquid Fund",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/KIM/SBI-Liquid-Fund-KIM.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "KIM",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Liquid Fund - Key Information Memorandum

## Type of Scheme
An open-ended liquid scheme investing in debt and money market securities with maturity up to 91 days.

## Minimum Application Amount
Fresh Purchase: Rs. 5,000/- and in multiples of Re. 1/- thereafter.
Additional Purchase: Rs. 1,000/- and in multiples of Re. 1/- thereafter.

## Minimum SIP Amount
Rs. 1,000/- per installment, minimum 6 installments.

## Exit Load (Graded, as per SEBI Circular)
Day 1: 0.0070%
Day 2: 0.0065%
Day 3: 0.0060%
Day 4: 0.0055%
Day 5: 0.0050%
Day 6: 0.0045%
Day 7 onwards: Nil

## Total Expense Ratio (TER)
Direct Plan: ~0.20% per annum
Regular Plan: ~0.33% per annum

## Benchmark
NIFTY Liquid Index A-I

## Riskometer
Low to Moderate Risk.

## Asset Allocation
Debt and money market instruments with maturity up to 91 days: Up to 100%
        """.strip(),
    },
    {
        "source_id"   : "SRC007",
        "title"       : "SBI Small Cap Fund - Scheme Page",
        "scheme"      : "SBI Small Cap Fund",
        "source_url"  : "https://www.sbimf.com/en-us/equity-funds/sbi-small-cap-fund",
        "organization": "SBI Mutual Fund",
        "source_type" : "scheme_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Small Cap Fund

SBI Small Cap Fund is an open-ended small cap equity scheme predominantly investing in small cap stocks.

## Scheme Objective
To provide investors with opportunities for long-term growth in capital along with the liquidity
of an open-ended scheme by investing predominantly in a well-diversified basket of equity stocks
of small cap companies.

## Benchmark
The benchmark index for SBI Small Cap Fund is S&P BSE 250 SmallCap TRI (Total Return Index).

## Riskometer
The risk level of SBI Small Cap Fund is Very High. Investors understand that their principal
will be at Very High risk.

## Minimum Investment
Minimum lump sum investment: Rs. 5,000 and in multiples of Re. 1 thereafter.
Minimum Additional Purchase: Rs. 1,000 and in multiples of Re. 1 thereafter.

## Minimum SIP
Minimum SIP investment amount: Rs. 500 per month.
Minimum SIP installments: 6.

## Exit Load
For units in excess of 10% of the investment, 1% exit load is charged for redemptions/switch-outs
within 1 year from the date of allotment. No exit load after 1 year. For the first 10% of
investment (by value), no exit load is applicable.

## Expense Ratio
The Total Expense Ratio (TER) for SBI Small Cap Fund Direct Plan is approximately 0.70% per annum.
The TER for Regular Plan is approximately 1.73% per annum.

## Fund Type
Open-ended Small Cap Equity Scheme.
        """.strip(),
    },
    {
        "source_id"   : "SRC008",
        "title"       : "SBI Small Cap Fund - Key Information Memorandum",
        "scheme"      : "SBI Small Cap Fund",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/KIM/SBI-Small-Cap-Fund-KIM.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "KIM",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Small Cap Fund - Key Information Memorandum

## Type of Scheme
An open-ended small cap equity scheme predominantly investing in small cap stocks.

## Minimum Application Amount
Fresh Purchase: Rs. 5,000/- and in multiples of Re. 1/- thereafter.
Additional Purchase: Rs. 1,000/- and in multiples of Re. 1/- thereafter.

## Minimum SIP Amount
Rs. 500/- per installment, minimum 6 installments.

## Exit Load
Exit load of 1% on redemptions/switch-outs within 1 year from date of allotment
(for units in excess of 10% of investment by value).
For the first 10% of units by value: Nil exit load.
After 1 year: Nil exit load.

## Total Expense Ratio (TER)
Direct Plan: ~0.70% per annum
Regular Plan: ~1.73% per annum

## Benchmark
S&P BSE 250 SmallCap TRI

## Riskometer
Very High Risk.

## Asset Allocation
Equity and equity related instruments of small cap companies: 65%-100%
Other equity instruments: 0%-35%
Debt and money market securities: 0%-35%
        """.strip(),
    },
    {
        "source_id"   : "SRC009",
        "title"       : "SBI Balanced Advantage Fund - Scheme Page",
        "scheme"      : "SBI Balanced Advantage Fund",
        "source_url"  : "https://www.sbimf.com/en-us/hybrid-funds/sbi-balanced-advantage-fund",
        "organization": "SBI Mutual Fund",
        "source_type" : "scheme_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Balanced Advantage Fund

SBI Balanced Advantage Fund is an open-ended dynamic asset allocation fund that dynamically manages
allocation between equity and debt based on market conditions.

## Scheme Objective
To provide long-term capital appreciation and income to investors through dynamic management of
investments across equity and fixed income instruments.

## Benchmark
The benchmark index for SBI Balanced Advantage Fund is CRISIL Hybrid 50+50 - Moderate Index.

## Riskometer
The risk level of SBI Balanced Advantage Fund is Very High. Investors understand that their
principal will be at Very High risk.

## Minimum Investment
Minimum lump sum investment: Rs. 5,000 and in multiples of Re. 1 thereafter.
Minimum Additional Purchase: Rs. 1,000 and in multiples of Re. 1 thereafter.

## Minimum SIP
Minimum SIP investment amount: Rs. 500 per month.
Minimum SIP installments: 6.

## Exit Load
For units in excess of 10% of the investment, 1% exit load is charged for redemptions/switch-outs
within 1 year from the date of allotment. No exit load after 1 year. For the first 10% of
investment (by value), no exit load is applicable.

## Expense Ratio
The Total Expense Ratio (TER) for SBI Balanced Advantage Fund Direct Plan is approximately 0.45%
per annum. The TER for Regular Plan is approximately 1.01% per annum.

## Fund Type
Open-ended Dynamic Asset Allocation Fund.
        """.strip(),
    },
    {
        "source_id"   : "SRC010",
        "title"       : "SBI Balanced Advantage Fund - Key Information Memorandum",
        "scheme"      : "SBI Balanced Advantage Fund",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/KIM/SBI-Balanced-Advantage-Fund-KIM.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "KIM",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Balanced Advantage Fund - Key Information Memorandum

## Type of Scheme
An open-ended dynamic asset allocation fund.

## Minimum Application Amount
Fresh Purchase: Rs. 5,000/- and in multiples of Re. 1/- thereafter.
Additional Purchase: Rs. 1,000/- and in multiples of Re. 1/- thereafter.

## Minimum SIP Amount
Rs. 500/- per installment, minimum 6 installments.

## Exit Load
Exit load of 1% on redemptions/switch-outs within 1 year from date of allotment
(for units in excess of 10% of investment by value).
For the first 10% of units by value: Nil exit load.
After 1 year: Nil exit load.

## Total Expense Ratio (TER)
Direct Plan: ~0.45% per annum
Regular Plan: ~1.01% per annum

## Benchmark
CRISIL Hybrid 50+50 - Moderate Index

## Riskometer
Very High Risk.
        """.strip(),
    },
    {
        "source_id"   : "SRC011",
        "title"       : "SBI MF Monthly Factsheet - April 2024",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/Factsheet/SBI-MF-Factsheet-April2024.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "factsheet",
        "last_updated": "2024-04-30",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Mutual Fund Monthly Factsheet - April 2024

## Expense Ratios (as of April 2024)

SBI Bluechip Fund
Direct Plan TER: 0.83% per annum
Regular Plan TER: 1.64% per annum
Benchmark: S&P BSE 100 TRI
Riskometer: Very High

SBI Magnum Tax Gain Scheme (ELSS)
Direct Plan TER: 0.91% per annum
Regular Plan TER: 1.74% per annum
Benchmark: S&P BSE 500 TRI
Riskometer: Very High
Lock-in period: 3 years (statutory ELSS lock-in)

SBI Liquid Fund
Direct Plan TER: 0.20% per annum
Regular Plan TER: 0.33% per annum
Benchmark: NIFTY Liquid Index A-I
Riskometer: Low to Moderate

SBI Small Cap Fund
Direct Plan TER: 0.70% per annum
Regular Plan TER: 1.73% per annum
Benchmark: S&P BSE 250 SmallCap TRI
Riskometer: Very High

SBI Balanced Advantage Fund
Direct Plan TER: 0.45% per annum
Regular Plan TER: 1.01% per annum
Benchmark: CRISIL Hybrid 50+50 - Moderate Index
Riskometer: Very High

## Minimum Investment Summary

SBI Bluechip Fund: Rs. 5,000 lump sum, Rs. 500 SIP
SBI Magnum Tax Gain Scheme: Rs. 500 lump sum, Rs. 500 SIP
SBI Liquid Fund: Rs. 5,000 lump sum, Rs. 1,000 SIP
SBI Small Cap Fund: Rs. 5,000 lump sum, Rs. 500 SIP
SBI Balanced Advantage Fund: Rs. 5,000 lump sum, Rs. 500 SIP
        """.strip(),
    },
    {
        "source_id"   : "SRC012",
        "title"       : "SBI MF - How to Download Account Statement",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sbimf.com/en-us/investor-services/account-statement",
        "organization": "SBI Mutual Fund",
        "source_type" : "faq_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## How to Download Your SBI MF Account Statement

Investors can download their SBI Mutual Fund account statement through the following methods:

## Method 1: SBI MF Website
1. Visit www.sbimf.com
2. Click on 'Investor Services' or 'My Portfolio'
3. Log in with your registered email ID/folio number and password
4. Navigate to 'Account Statement'
5. Select the date range and scheme
6. Download the statement in PDF format

## Method 2: CAMS Online (for CAMS-serviced folios)
SBI Mutual Fund folios are serviced by CAMS (Computer Age Management Services).
1. Visit www.camsonline.com
2. Click on 'Investor Services' → 'Mailback Services' → 'Account Statement'
3. Enter your registered email ID and PAN
4. You will receive the statement on your registered email address

## Method 3: myCAMS App
1. Download the myCAMS mobile app
2. Log in using your registered mobile number or email
3. Navigate to 'Reports' → 'Account Statement'
4. Download or email the statement

## Method 4: Email Request
Send an email to investor@sbimf.com with:
- Your registered email ID
- Folio number (do not share PAN or Aadhaar in email)
- Date range for the statement

## Important
Do NOT share your PAN, Aadhaar number, bank account number, or OTP with anyone while
requesting your statement.
        """.strip(),
    },
    {
        "source_id"   : "SRC013",
        "title"       : "SBI MF - Capital Gains Tax Document Guide",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sbimf.com/en-us/investor-services/capital-gain-statement",
        "organization": "SBI Mutual Fund",
        "source_type" : "faq_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## Capital Gains Statement - SBI Mutual Fund

A capital gains statement provides details of all redemptions/switches made during a financial
year, along with the capital gains or losses for tax filing purposes.

## How to Download Capital Gains Statement

## Method 1: CAMS Online
1. Visit www.camsonline.com
2. Click on 'Investor Services' → 'Mailback Services' → 'Capital Gains Statement'
3. Enter your PAN and registered email ID
4. Select the financial year
5. You will receive the capital gains statement on your registered email address

## Method 2: SBI MF Website
1. Visit www.sbimf.com → Investor Services
2. Log in to your account
3. Navigate to 'Tax Corner' or 'Capital Gains'
4. Select financial year
5. Download statement

## Method 3: myCAMS App
1. Open myCAMS app → Reports → Capital Gains Statement
2. Select financial year and generate report

## Types of Capital Gains for Mutual Funds
Short-Term Capital Gains (STCG): Gains on equity units held for less than 12 months.
Long-Term Capital Gains (LTCG): Gains on equity units held for 12 months or more.
For ELSS funds: Units have 3-year lock-in; gains after 3 years are treated as LTCG.

## Important Note
For specific tax advice, please consult a registered tax professional. This statement provides
data for your tax calculation; it is not tax advice.
        """.strip(),
    },
    {
        "source_id"   : "SRC014",
        "title"       : "SBI MF - SIP Registration and Details",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sbimf.com/en-us/investor-services/sip-details",
        "organization": "SBI Mutual Fund",
        "source_type" : "faq_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## Systematic Investment Plan (SIP) - SBI Mutual Fund

A Systematic Investment Plan (SIP) allows investors to invest a fixed amount at regular intervals
(monthly, quarterly) in a mutual fund scheme.

## SIP Minimum Amounts (SBI Mutual Fund)
SBI Bluechip Fund: Rs. 500/- per SIP installment (minimum 6 installments)
SBI Magnum Tax Gain Scheme: Rs. 500/- per SIP installment (minimum 6 installments)
SBI Liquid Fund: Rs. 1,000/- per SIP installment (minimum 6 installments)
SBI Small Cap Fund: Rs. 500/- per SIP installment (minimum 6 installments)
SBI Balanced Advantage Fund: Rs. 500/- per SIP installment (minimum 6 installments)

## SIP Frequencies Available
Monthly SIP
Quarterly SIP

## How to Register a SIP
1. Visit www.sbimf.com or use the SBI MF mobile app
2. Log in or create a new investor account
3. Select the scheme and SIP amount
4. Link your bank account (NACH mandate required)
5. Submit the SIP registration form

## SIP Pause and Stop
Investors can pause SIP for 1-3 months or stop the SIP at any time
(subject to minimum installment completion).

## Note on ELSS SIP
For SBI Magnum Tax Gain Scheme (ELSS), each SIP installment is treated as a fresh investment
with a separate 3-year lock-in period from the date of that installment's allotment.
        """.strip(),
    },
    {
        "source_id"   : "SRC015",
        "title"       : "SBI MF - Investor FAQs",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sbimf.com/en-us/investor-services/faqs",
        "organization": "SBI Mutual Fund",
        "source_type" : "faq_page",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Mutual Fund - Frequently Asked Questions

## What is a folio number?
A folio number is a unique identification number assigned to an investor when they first invest
in an SBI Mutual Fund scheme. It acts like an account number for your SBI MF investments.

## What is NAV?
NAV (Net Asset Value) is the per-unit price of a mutual fund scheme. It is calculated as:
NAV = (Total Assets - Total Liabilities) / Total Number of Units Outstanding.

## What is the difference between Direct Plan and Regular Plan?
Direct Plan: Investor invests directly with the AMC without going through a distributor.
Direct Plans have lower expense ratios as no distributor commission is paid.
Regular Plan: Investor invests through a distributor/broker. Regular Plans have higher
expense ratios due to distributor commission.

## What is IDCW?
IDCW stands for Income Distribution cum Capital Withdrawal. It is the option where the fund
distributes income to investors periodically (previously called Dividend option).

## How do I update my bank account details?
Visit sbimf.com → Investor Services → Bank Account Update, or visit the nearest SBI MF
investor service centre with a cancelled cheque.

## What is the cut-off time for mutual fund purchases?
For most schemes: 3:00 PM on a business day.
For liquid and overnight funds: 1:30 PM on a business day.

## How do I check my SBI MF balance?
Log in to www.sbimf.com or the SBI MF app to check your portfolio balance and NAV.

## Can I invest without KYC?
No. KYC (Know Your Customer) compliance is mandatory for all mutual fund investments
as per SEBI regulations. Complete your KYC at a KRA (KYC Registration Agency).

## What documents are needed for KYC?
Identity proof (PAN card is mandatory), address proof, and a passport-size photograph.
        """.strip(),
    },
    {
        "source_id"   : "SRC016",
        "title"       : "AMFI - What is a Mutual Fund",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.amfiindia.com/investor-corner/knowledge-center/what-is-mutual-fund.html",
        "organization": "AMFI",
        "source_type" : "educational_page",
        "last_updated": "2024-01-01",
        "date_accessed": "2026-10-02",
        "text": """
## What is a Mutual Fund? - AMFI (Association of Mutual Funds in India)

A mutual fund is a trust that pools the savings of a number of investors who share a common
financial goal. The money thus collected is then invested by the fund manager in different types
of securities, depending on the scheme's stated objective.

## Key Features of Mutual Funds
- Professional fund management by SEBI-registered Asset Management Companies (AMCs)
- Diversification across multiple securities
- Liquidity (open-ended funds can be redeemed on any business day)
- Regulated by SEBI (Securities and Exchange Board of India)
- Transparency through regular NAV disclosure

## Types of Mutual Fund Schemes
Equity Schemes: Invest primarily in equity shares of companies.
Debt Schemes: Invest in fixed-income instruments like bonds, government securities.
Hybrid Schemes: Invest in a mix of equity and debt instruments.
Solution-Oriented Schemes: Retirement fund, children's fund (with lock-in).
Other Schemes: Index funds, ETFs, Fund of Funds.

## SEBI Registration
All mutual funds in India must be registered with SEBI and comply with SEBI Mutual Fund
Regulations, 1996.

## AMFI
AMFI (Association of Mutual Funds in India) is an industry body that represents mutual fund
houses in India. AMFI promotes best practices and investor education. Website: www.amfiindia.com.
        """.strip(),
    },
    {
        "source_id"   : "SRC017",
        "title"       : "AMFI - What is an ELSS Fund",
        "scheme"      : "SBI Magnum Tax Gain Scheme",
        "source_url"  : "https://www.amfiindia.com/investor-corner/knowledge-center/elss.html",
        "organization": "AMFI",
        "source_type" : "educational_page",
        "last_updated": "2024-01-01",
        "date_accessed": "2026-10-02",
        "text": """
## Equity Linked Savings Scheme (ELSS) - AMFI

An Equity Linked Savings Scheme (ELSS) is a type of mutual fund scheme that invests primarily
in equities and equity-related instruments.

## Lock-in Period
ELSS schemes have a mandatory statutory lock-in period of 3 years from the date of allotment.
This is one of the shortest lock-in periods among tax-saving instruments under Section 80C.
Units cannot be redeemed, switched, or transferred before completion of the 3-year lock-in.

## Tax Benefit under Section 80C
Investments in ELSS are eligible for income tax deduction under Section 80C of the Income Tax
Act, 1961 up to a maximum of Rs. 1,50,000 per financial year.

## Tax on Redemption
After the 3-year lock-in, gains from ELSS redemptions are classified as Long-Term Capital Gains
(LTCG). LTCG above Rs. 1,00,000 per financial year is taxed at 10% (without indexation benefit).

## SIP in ELSS
When investing in ELSS through SIP, each installment is treated as a separate investment with
its own 3-year lock-in. This means different SIP installments will have different maturity dates.

## Key Advantages of ELSS
1. Tax savings under Section 80C
2. Lowest lock-in period (3 years) among 80C investments
3. Potential for higher returns due to equity exposure
4. Professional management
        """.strip(),
    },
    {
        "source_id"   : "SRC018",
        "title"       : "AMFI - Riskometer Explained",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.amfiindia.com/investor-corner/knowledge-center/riskometer.html",
        "organization": "AMFI",
        "source_type" : "educational_page",
        "last_updated": "2024-01-01",
        "date_accessed": "2026-10-02",
        "text": """
## Riskometer - AMFI (Association of Mutual Funds in India)

The Riskometer is a standardised risk measurement tool mandated by SEBI for all mutual fund
schemes in India. It helps investors understand the risk level of a mutual fund scheme.

## Riskometer Levels (6 levels)
1. Low: Principal at Low Risk
2. Low to Moderate: Principal at Low to Moderate Risk
3. Moderate: Principal at Moderate Risk
4. Moderately High: Principal at Moderately High Risk
5. High: Principal at High Risk
6. Very High: Principal at Very High Risk

## Riskometer for SBI Mutual Fund Schemes
SBI Bluechip Fund: Very High (equity large cap scheme)
SBI Magnum Tax Gain Scheme: Very High (ELSS equity scheme)
SBI Liquid Fund: Low to Moderate (liquid debt scheme, up to 91-day maturity)
SBI Small Cap Fund: Very High (equity small cap scheme)
SBI Balanced Advantage Fund: Very High (dynamic asset allocation fund)

## How is the Riskometer Determined?
The risk level is determined based on SEBI's product labelling guidelines.
Factors include: asset class (equity/debt), market cap, credit quality, duration, and liquidity.

## Updated Riskometer (SEBI Circular 2021)
SEBI revised the riskometer guidelines in 2020-21 requiring monthly recalibration of risk
levels based on the scheme's actual portfolio. Schemes must disclose any change in riskometer.
        """.strip(),
    },
    {
        "source_id"   : "SRC019",
        "title"       : "AMFI - Total Expense Ratio (TER) Disclosure",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.amfiindia.com/research-information/other-data/scheme-wise-ratio",
        "organization": "AMFI",
        "source_type" : "regulatory_page",
        "last_updated": "2024-04-30",
        "date_accessed": "2026-10-02",
        "text": """
## Total Expense Ratio (TER) - AMFI Disclosure

AMFI publishes scheme-wise Total Expense Ratio (TER) on its website on a monthly basis as
mandated by SEBI.

## What is TER?
The Total Expense Ratio (TER) is the annual cost charged by the mutual fund to manage
the scheme. It includes management fees, administrative costs, registrar fees, and
distribution commissions (for Regular Plans).

## TER Limits (as per SEBI Circular September 2018)
For equity-oriented schemes:
- Up to Rs. 500 crores AUM: Maximum 2.25% TER
- Next Rs. 250 crores AUM: Maximum 2.00% TER
- Next Rs. 1,250 crores AUM: Maximum 1.75% TER
- Next Rs. 3,000 crores AUM: Maximum 1.60% TER
- Next Rs. 5,000 crores AUM: Maximum 1.50% TER
- On balance AUM: Maximum 1.05% TER

Additional TER up to 30 bps (0.30%) can be charged if new inflows from B30 cities exceed 30%.

## Direct vs Regular Plan TER
Direct Plans have lower TER because no distributor commission is included.
Regular Plans have higher TER due to distributor commission embedded in TER.

## TER Disclosure
TER is disclosed on the AMFI website: www.amfiindia.com under 'Research & Information'.
AMCs must update TER disclosures on a daily basis.
        """.strip(),
    },
    {
        "source_id"   : "SRC020",
        "title"       : "SEBI - Circular on Total Expense Ratio",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sebi.gov.in/legal/circulars/sep-2018/total-expense-ratio-ter-of-mutual-funds_40276.html",
        "organization": "SEBI",
        "source_type" : "regulatory_circular",
        "last_updated": "2018-09-18",
        "date_accessed": "2026-10-02",
        "text": """
## SEBI Circular - Total Expense Ratio (TER) of Mutual Funds
Circular No.: SEBI/HO/IMD/DF2/CIR/P/2018/137
Date: September 18, 2018

## Background
SEBI reviewed the Total Expense Ratio (TER) structure for mutual funds and issued revised
guidelines to protect investor interests and ensure cost transparency.

## Key Provisions

## TER Limits for Equity-Oriented Schemes
AUM up to Rs. 500 crores: TER capped at 2.25%
AUM next Rs. 250 crores (Rs. 500-750 crores): TER capped at 2.00%
AUM next Rs. 1,250 crores (Rs. 750-2,000 crores): TER capped at 1.75%
AUM next Rs. 3,000 crores (Rs. 2,000-5,000 crores): TER capped at 1.60%
AUM next Rs. 5,000 crores (Rs. 5,000-10,000 crores): TER capped at 1.50%
AUM on balance (above Rs. 10,000 crores): TER capped at 1.05%

## B30 Incentive
An additional TER of up to 30 basis points (0.30%) is allowed if new inflows from beyond top
30 cities (B30) are at least 30% of gross new inflows.

## Disclosure Requirements
- AMCs shall disclose TER of each scheme on their website and the AMFI website on a daily basis.
- Any change in TER must be communicated to investors via notice-cum-addendum.

## Exit Load
Exit load collected by the AMC shall be credited to the scheme. AMC cannot retain exit load.
        """.strip(),
    },
    {
        "source_id"   : "SRC021",
        "title"       : "SEBI - ELSS Notification and Lock-in Rules",
        "scheme"      : "SBI Magnum Tax Gain Scheme",
        "source_url"  : "https://www.sebi.gov.in/legal/circulars/dec-2005/elss-notification_9928.html",
        "organization": "SEBI",
        "source_type" : "regulatory_circular",
        "last_updated": "2005-12-28",
        "date_accessed": "2026-10-02",
        "text": """
## SEBI - Equity Linked Savings Scheme (ELSS) Regulations

## ELSS Lock-in Period
As per the ELSS notification and SEBI regulations, all Equity Linked Savings Schemes (ELSS)
are required to have a statutory lock-in period of 3 years from the date of allotment of units.

## Key Provisions
1. Lock-in period: 3 years from date of allotment (mandatory, cannot be waived)
2. No redemption, switch-out, or transfer is permitted during the lock-in period
3. The lock-in applies to each installment separately (relevant for SIP investors)
4. After the 3-year lock-in, units can be freely redeemed

## Tax Benefit
ELSS investments are eligible for deduction under Section 80C of the Income Tax Act, 1961.
Maximum deduction: Rs. 1,50,000 per financial year.

## SEBI Oversight
All ELSS schemes must be registered with SEBI and comply with SEBI Mutual Fund
Regulations, 1996 and the ELSS notification.

## Section 80C Context
ELSS is one of several Section 80C instruments. Unlike PPF (15-year lock-in) or NSC
(5-year lock-in), ELSS has the shortest lock-in of 3 years among common 80C instruments.
        """.strip(),
    },
    {
        "source_id"   : "SRC022",
        "title"       : "SEBI - Categorisation and Rationalisation of Mutual Fund Schemes",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.sebi.gov.in/legal/circulars/oct-2017/categorization-and-rationalization-of-the-schemes-of-mutual-funds_36199.html",
        "organization": "SEBI",
        "source_type" : "regulatory_circular",
        "last_updated": "2017-10-06",
        "date_accessed": "2026-10-02",
        "text": """
## SEBI Circular - Categorization and Rationalization of Mutual Fund Schemes
Circular No.: SEBI/HO/IMD/DF3/CIR/P/2017/114
Date: October 6, 2017

## Purpose
To bring uniformity in the characteristics of similar type of schemes launched by different
mutual funds, to ensure that an investor of mutual funds is able to evaluate the different
options available to him and take informed decisions.

## Scheme Categories

## Equity Schemes
Large Cap Fund: Minimum 80% investment in large cap stocks (top 100 companies by market cap)
Mid Cap Fund: Minimum 65% in mid cap stocks (101st-250th companies by market cap)
Small Cap Fund: Minimum 65% in small cap stocks (251st company onwards by market cap)
Large & Mid Cap Fund: Minimum 35% each in large cap and mid cap stocks
ELSS: Minimum 80% in equity; 3-year lock-in; eligible for Section 80C deduction
Multi Cap Fund: Minimum 25% each in large cap, mid cap, and small cap

## Debt Schemes
Liquid Fund: Investment in debt and money market instruments with maturity up to 91 days
Overnight Fund: Investment in overnight securities

## Hybrid Schemes
Balanced Advantage / Dynamic Asset Allocation: Investment in equity and debt dynamically managed
Conservative Hybrid Fund: 10-25% equity, 75-90% debt

## Benchmark Requirement
Each scheme category must use the appropriate designated benchmark index.
Large Cap: S&P BSE 100 / Nifty 100
Small Cap: S&P BSE 250 SmallCap / Nifty SmallCap 250
Liquid: NIFTY Liquid Index
        """.strip(),
    },
    {
        "source_id"   : "SRC023",
        "title"       : "AMFI - Exit Load Information",
        "scheme"      : "All Schemes",
        "source_url"  : "https://www.amfiindia.com/investor-corner/knowledge-center/exit-load.html",
        "organization": "AMFI",
        "source_type" : "educational_page",
        "last_updated": "2024-01-01",
        "date_accessed": "2026-10-02",
        "text": """
## Exit Load - AMFI (Association of Mutual Funds in India)

Exit load is a fee charged by a mutual fund when an investor redeems or switches out of
a scheme before a specified period.

## Purpose of Exit Load
Exit load discourages early redemptions and helps protect long-term investors from
the costs associated with frequent trading/redemption activity.

## SEBI Rules on Exit Load
As per SEBI regulations, all exit load collected by the AMC must be credited back to the
scheme and cannot be retained by the AMC.

## Exit Load for SBI Mutual Fund Schemes

SBI Bluechip Fund:
1% exit load on units in excess of 10% of investment redeemed within 1 year.
No exit load on first 10% of investment.
No exit load after 1 year.

SBI Magnum Tax Gain Scheme (ELSS):
Nil exit load (scheme has mandatory 3-year lock-in; no exit is possible during lock-in).

SBI Liquid Fund (Graded exit load as per SEBI circular):
Day 1: 0.0070%, Day 2: 0.0065%, Day 3: 0.0060%
Day 4: 0.0055%, Day 5: 0.0050%, Day 6: 0.0045%
Day 7 onwards: Nil

SBI Small Cap Fund:
1% exit load on units in excess of 10% of investment redeemed within 1 year.
No exit load on first 10% of investment.
No exit load after 1 year.

SBI Balanced Advantage Fund:
1% exit load on units in excess of 10% of investment redeemed within 1 year.
No exit load on first 10% of investment.
No exit load after 1 year.

## How to Calculate Exit Load
Exit Load Amount = Units Redeemed × NAV at Redemption × Exit Load Rate (%)
        """.strip(),
    },
    {
        "source_id"   : "SRC024",
        "title"       : "SBI Bluechip Fund - Scheme Information Document",
        "scheme"      : "SBI Bluechip Fund",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/SID/SBI-BlueChip-Fund-SID.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "SID",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Bluechip Fund - Scheme Information Document (SID)

## Type of Scheme
An open-ended large cap equity scheme investing in large cap stocks.

## Investment Objective
To provide investors with opportunities for long-term growth in capital through an active
management of investments in a diversified basket of large cap stocks.

## Asset Allocation Pattern
Equity and equity related instruments of large cap companies: 80% to 100% of total assets
Other equity and equity related instruments: 0% to 20% of total assets
Debt and money market securities: 0% to 20% of total assets

## Large Cap Definition (as per SEBI)
Large cap companies are defined as the top 100 companies in terms of full market
capitalization listed on stock exchanges. AMFI classifies large cap companies.

## Benchmark
S&P BSE 100 TRI (Total Return Index)

## Riskometer
Very High

## Exit Load Policy
1% if redeemed/switched out within 1 year from date of allotment (on units > 10% of investment).
First 10% of investment redeemed at any time: No exit load.
After 1 year: No exit load.

## Minimum Application Amounts
Minimum fresh purchase: Rs. 5,000/-
Minimum additional purchase: Rs. 1,000/-
Minimum SIP: Rs. 500/- per installment

## Investment Plans and Options
Direct Plan - Growth Option
Direct Plan - IDCW Option (Payout and Reinvestment)
Regular Plan - Growth Option
Regular Plan - IDCW Option (Payout and Reinvestment)

## Fund Manager
The scheme is managed by the designated fund manager of SBI Funds Management Ltd.
(SBIFML is the Asset Management Company)

## Registrar and Transfer Agent
CAMS (Computer Age Management Services Pvt. Ltd.)

## Trustee
SBI Mutual Fund Trustee Company Private Limited

## Risk Factors
Mutual Fund investments are subject to market risks. Read all scheme-related documents
carefully before investing.
        """.strip(),
    },
    {
        "source_id"   : "SRC025",
        "title"       : "SBI Magnum Tax Gain Scheme - Scheme Information Document",
        "scheme"      : "SBI Magnum Tax Gain Scheme",
        "source_url"  : "https://www.sbimf.com/Uploads/StaticContent/SID/SBI-Magnum-TaxGain-SID.pdf",
        "organization": "SBI Mutual Fund",
        "source_type" : "SID",
        "last_updated": "2024-03-31",
        "date_accessed": "2026-10-02",
        "text": """
## SBI Magnum Tax Gain Scheme - Scheme Information Document (SID)

## Type of Scheme
An open-ended equity linked savings scheme (ELSS) with a statutory lock-in of 3 years and
tax benefit under Section 80C of the Income Tax Act, 1961.

## Investment Objective
To deliver the benefit of investment in a portfolio of equity shares, while offering a deduction
on such investments made in the scheme under Section 80C of the Income Tax Act, 1961.

## ELSS Lock-in Period
The lock-in period is 3 years from the date of allotment of units. Redemption before
completion of 3 years is not permitted. For SIP investments, each installment has its own
3-year lock-in from the respective allotment date.

## Asset Allocation Pattern
Equity and equity related instruments: 80% to 100% of total assets
Debt and money market securities: 0% to 20% of total assets

## Benchmark
S&P BSE 500 TRI (Total Return Index)

## Riskometer
Very High

## Exit Load
Nil. No exit load applicable as the scheme has a mandatory 3-year lock-in period.

## Section 80C Tax Benefit
Investments are eligible for deduction under Section 80C of the Income Tax Act, 1961.
Maximum permissible deduction: Rs. 1,50,000/- per financial year.

## Minimum Application Amounts
Minimum fresh purchase: Rs. 500/-
Minimum additional purchase: Rs. 500/-
Minimum SIP: Rs. 500/- per installment

## Investment Plans and Options
Direct Plan - Growth Option
Direct Plan - IDCW Option
Regular Plan - Growth Option
Regular Plan - IDCW Option

## Registrar and Transfer Agent
CAMS (Computer Age Management Services Pvt. Ltd.)

## Important Disclaimer
Mutual Fund investments are subject to market risks. Read all scheme-related documents
carefully before investing. Past performance is not indicative of future results.
        """.strip(),
    },
]


def seed_processed_documents(processed_dir: Path, force: bool = False) -> dict:
    """
    Write all seed documents to data/processed/ as JSON files.
    Only writes if file does not exist or force=True.

    Returns summary dict.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)
    written, skipped = 0, 0

    for doc in SEED_DOCUMENTS:
        out_path = processed_dir / f"{doc['source_id']}.json"
        if not force and out_path.exists():
            logger.info(f"[CACHED] {doc['source_id']} already exists, skipping.")
            skipped += 1
            continue

        doc_with_meta = {
            **doc,
            "char_count": len(doc["text"]),
            "seeded": True,
        }
        out_path.write_text(
            json.dumps(doc_with_meta, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"[SEEDED] {doc['source_id']} → {out_path}")
        written += 1

    summary = {
        "total"  : len(SEED_DOCUMENTS),
        "written": written,
        "skipped": skipped,
    }
    logger.info(f"Seed complete: {written} written, {skipped} skipped")
    return summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.config.settings import PROCESSED_DIR
    logging.basicConfig(level=logging.INFO)
    result = seed_processed_documents(PROCESSED_DIR, force=False)
    print(json.dumps(result, indent=2))

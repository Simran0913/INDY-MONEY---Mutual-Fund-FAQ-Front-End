# Sample Q&A
## Facts-Only Mutual Fund FAQ Assistant

These sample answers demonstrate the expected output format of the RAG system.
All answers are grounded in official sources. No invented facts.

---

## Factual Q&A Examples

---

**Question:** What is the expense ratio of SBI Bluechip Fund?

**Answer:** The Total Expense Ratio (TER) for SBI Bluechip Fund Direct Plan is approximately 0.83% per annum, and the Regular Plan TER is approximately 1.64% per annum. TER is disclosed on the AMFI website and updated monthly. Direct Plans have lower TER because no distributor commission is included.

**Source:** https://www.sbimf.com/en-us/equity-funds/sbi-bluechip-fund

**Last updated from sources:** 2024-03-31

---

**Question:** What is the exit load for SBI Small Cap Fund?

**Answer:** SBI Small Cap Fund charges an exit load of 1% for units redeemed or switched out within 1 year from the date of allotment, applicable on units in excess of 10% of investment by value. The first 10% of investment redeemed at any time attracts no exit load. After 1 year from the date of allotment, no exit load is charged.

**Source:** https://www.sbimf.com/en-us/equity-funds/sbi-small-cap-fund

**Last updated from sources:** 2024-03-31

---

**Question:** What is the minimum SIP for SBI Magnum Tax Gain Scheme?

**Answer:** The minimum SIP investment amount for SBI Magnum Tax Gain Scheme is Rs. 500 per installment, with a minimum of 6 installments required. For ELSS SIP investments, each installment is treated as a fresh purchase with its own separate 3-year lock-in period from the date of that installment's allotment. SIP can be registered on a monthly or quarterly frequency.

**Source:** https://www.sbimf.com/en-us/investor-services/sip-details

**Last updated from sources:** 2024-03-31

---

**Question:** What is the ELSS lock-in period for SBI Magnum Tax Gain Scheme?

**Answer:** The statutory lock-in period for SBI Magnum Tax Gain Scheme is 3 years from the date of allotment of units. Units cannot be redeemed, switched, or transferred before completion of this 3-year lock-in period, as mandated by SEBI regulations for all ELSS schemes. This is one of the shortest lock-in periods among tax-saving instruments under Section 80C.

**Source:** https://www.amfiindia.com/investor-corner/knowledge-center/elss.html

**Last updated from sources:** 2024-01-01

---

**Question:** What is the riskometer of SBI Liquid Fund?

**Answer:** The riskometer risk level for SBI Liquid Fund is Low to Moderate. This means investors understand that their principal will be at Low to Moderate risk. The low risk level is because SBI Liquid Fund invests only in debt and money market instruments with maturity up to 91 days.

**Source:** https://www.amfiindia.com/investor-corner/knowledge-center/riskometer.html

**Last updated from sources:** 2024-01-01

---

**Question:** What is the benchmark for SBI Bluechip Fund?

**Answer:** The benchmark index for SBI Bluechip Fund is S&P BSE 100 TRI (Total Return Index). The S&P BSE 100 represents the top 100 companies by market capitalisation listed on BSE, consistent with SEBI's definition of large cap companies. This benchmark is used to evaluate the performance of the scheme.

**Source:** https://www.sbimf.com/en-us/equity-funds/sbi-bluechip-fund

**Last updated from sources:** 2024-03-31

---

**Question:** How can I download my SBI MF account statement?

**Answer:** You can download your SBI Mutual Fund account statement by logging into www.sbimf.com under Investor Services → Account Statement, or through CAMS online at www.camsonline.com under Mailback Services → Account Statement. The myCAMS mobile app also provides account statements under Reports. Please do not share personal information (PAN, Aadhaar, OTP) while accessing your statement.

**Source:** https://www.sbimf.com/en-us/investor-services/account-statement

**Last updated from sources:** 2024-03-31

---

**Question:** Where can I find the capital gains statement for SBI Mutual Fund?

**Answer:** The capital gains statement for SBI Mutual Fund can be downloaded from CAMS online (www.camsonline.com) under Investor Services → Mailback Services → Capital Gains Statement, or via the SBI MF website under Investor Services → Tax Corner. You can also access it through the myCAMS mobile app under Reports → Capital Gains Statement. Select the relevant financial year to generate your statement.

**Source:** https://www.sbimf.com/en-us/investor-services/capital-gain-statement

**Last updated from sources:** 2024-03-31

---

**Question:** What is the minimum investment in SBI Balanced Advantage Fund?

**Answer:** The minimum lump sum investment in SBI Balanced Advantage Fund is Rs. 5,000 with additional purchases of Rs. 1,000 or more. The minimum SIP amount is Rs. 500 per installment with a minimum of 6 installments. The scheme is available in Direct Plan and Regular Plan, each with Growth and IDCW options.

**Source:** https://www.sbimf.com/en-us/hybrid-funds/sbi-balanced-advantage-fund

**Last updated from sources:** 2024-03-31

---

## Safe Refusal Examples

---

**Question:** Should I buy SBI Bluechip Fund?

**Answer (Safe Refusal):** I can provide verified factual information about the scheme, but I can't provide investment advice or recommend whether you should buy, sell, or invest in any fund. For investment guidance, please consult a SEBI-registered investment advisor. You can find educational information about mutual funds at: https://www.amfiindia.com/investor-corner/knowledge-center

**Category:** INVESTMENT_ADVICE (Safe Refusal)

---

**Question:** Which SBI fund will give the highest return?

**Answer (Safe Refusal):** I can provide verified factual information about the scheme, but I can't provide investment advice or recommend whether you should buy, sell, or invest in any fund. Return predictions are not within the scope of this assistant. For investment guidance, please consult a SEBI-registered investment advisor.

**Category:** INVESTMENT_ADVICE (Safe Refusal)

---

**Question:** Can I give you my PAN number?

**Answer (PII Warning):** Please do not share personal information such as your PAN, Aadhaar number, bank account number, OTP, phone number, or email in this chat. This assistant only answers factual questions about mutual fund schemes. For account-related queries, please contact SBI MF directly at www.sbimf.com or call their investor helpline.

**Category:** PII_DETECTED (PII Warning)

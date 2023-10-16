insert into "Bills" (legislative_id, legislative_session, bill_number, session_type, chamber)
values(
   '20230HB1540',
   '2023',
   '1540',
   '0',
   'HOUSE'
)

insert into "Revisions" (revision_guid, printer_no, full_text_link, publication_date, description, bill_internal_id)
values(
  '20230HB1540P2050',
  '2050',
  'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=1540&pn=2050',
  'Fri, 13 Oct 2023 13:04:20 GMT',
  'An Act amending the act of March 10, 1949 (P.L.30, No.14), known as the Public School Code of 1949, in terms and courses of study, further providing for Commission for Agricultural Education Excellence....',
  (SELECT bill_internal_id from "Bills" where legislative_id like '20230HB1540')
)
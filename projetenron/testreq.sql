SELECT t.emailadress_id_id, m.path
FROM app1_mail m
INNER JOIN app1_to t
    ON m.mail_id=t.mail_id_id
;
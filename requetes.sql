----Requête n°1----
SELECT *
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE e.lastname='Taylor' AND e.firstname='Mark'
;

SELECT e.firstname , e.lastname , e.category, e.mailbox, ea.emailadress_id
FROM (SELECT * /*Cette sous-requête a pour but de récupérer l'id de l'employé à partir de l'adresse mail*/
    FROM app1_employee e
    INNER JOIN app1_emailadress ea
        ON e.employee_id=ea.employee_id_id
    WHERE ea.emailadress_id='elizabeth.sager@enron.com') e
INNER JOIN app1_emailadress ea /*Puis ce join permet de récupérer toutes ces autres adresses mails*/
    ON e.employee_id=ea.employee_id_id
;

----Requête n°2----
SELECT * 
FROM app1_mail
WHERE Timedate > '2000-01-01 00:00:00'
;

----par mail envoyé----
SELECT lastname,firstname,nbmail FROM
    (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail   
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        INNER JOIN app1_mail m 
            ON m.emailadress_id_id=ea.emailadress_id
        WHERE Timedate > '2000-01-01 00:00:00'
        GROUP BY emp.employee_id
    ) T
    WHERE nbmail>40
;

----par mail reçu----
SELECT lastname,firstname,nbmail FROM
    (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail   
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        INNER JOIN app1_to t
            ON t.emailadress_id_id=ea.emailadress_id
        INNER JOIN app1_mail m 
            ON m.mail_id=t.mail_id_id
        WHERE Timedate > '2000-01-01 00:00:00'
        GROUP BY emp.employee_id
    ) T
    WHERE nbmail>100
;

----version où l'on peut filtrer les expéditeurs internes ou externes---- 
SELECT lastname,firstname,nbmail FROM
    (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail, m.interne   
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        INNER JOIN app1_to t
            ON t.emailadress_id_id=ea.emailadress_id
        INNER JOIN 
            (SELECT m.mail_id , ea2.interne
            FROM app1_mail m 
            INNER JOIN app1_emailadress ea2
                ON m.emailadress_id_id=ea2.emailadress_id
            WHERE m.Timedate > '2000-01-01 00:00:00'
            ) m
            ON m.mail_id=t.mail_id_id
        GROUP BY emp.employee_id, m.interne
    ) T
    WHERE nbmail>100
;


SELECT COUNT(*)
FROM app1_mail m 
INNER JOIN app1_emailadress ea
    ON m.emailadress_id_id=ea.emailadress_id
GROUP BY ea.interne 
;


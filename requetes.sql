----Requête n°1----
SELECT *
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE e.lastname='Taylor' AND e.firstname='Mark'
;

SELECT *
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE ea.emailadress_id='elizabeth.sager@enron.com'
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
        INNER JOIN (
            SELECT t.emailadress_id_id as ead
            FROM app1_to t
            INNER JOIN app1_mail m
                ON t.mail_id_id=m.mail_id 
        WHERE Timedate > '2001-01-01 00:00:00'
        ) t2
        ON t2.ead=ea.emailadress_id
        GROUP BY emp.employee_id
    ) T
    WHERE nbmail>100
;
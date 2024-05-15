SELECT * FROM app1_mail
    WHERE emailadress_id_id = 'keith.holst@enron.com'
;


DATE_TRUNC(interval, date)



SELECT * FROM app1_mail
    WHERE mail_id = '16048952.1075842024694.JavaMail.evans@thyme'
;

SELECT * FROM app1_mail
    WHERE timedate BETWEEN  '2001-08-01 09:00:00' AND '2001-08-01 09:30:00'
;

SELECT * FROM app1_mail
    WHERE path LIKE '/cash-m/ethics_ljm_notre_dame/1.'
;

SELECT COUNT(*) FROM (
SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
            LEFT JOIN 
            (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea /*Cette sous-requête récupère tout ce qui concerne les auteurs*/
                LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
            ON aut.emailadress_id=m.emailadress_id_id
            LEFT JOIN 
            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t /*Cette sous-requête permet de dire si un mail a été envoyé qu'à des destinataires internes ou s'il y a un destinataires externes dans le mail*/
                INNER JOIN app1_emailadress ea2 
                    ON t.emailadress_id_id=ea2.emailadress_id 
                GROUP BY t.mail_id_id ) dint 
            ON m.mail_id=dint.mail_id_id
            LEFT JOIN
            (SELECT t.mail_id_id, t.emailadress_id_id, eadest.firstname, eadest.lastname FROM app1_to t /*Cette sous-requête récupère tout ce qui concerne les destinataires*/
                LEFT JOIN 
                (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
                    LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
                ON t.emailadress_id_id=eadest.emailadress_id ) dest 
            ON m.mail_id=dest.mail_id_id
            GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate ) T ;


            WHERE m.Timedate > '2001-01-01' AND dest.firstname='Jeff' AND dest.lastname='King' AND aut.interne=True


SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
            LEFT JOIN 
            (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea /*Cette sous-requête récupère tout ce qui concerne les auteurs*/
                LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
            ON aut.emailadress_id=m.emailadress_id_id
            LEFT JOIN 
            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t /*Cette sous-requête permet de dire si un mail a été envoyé qu'à des destinataires internes ou s'il y a un destinataires externes dans le mail*/
                INNER JOIN app1_emailadress ea2 
                    ON t.emailadress_id_id=ea2.emailadress_id 
                GROUP BY t.mail_id_id ) dint 
            ON m.mail_id=dint.mail_id_id
            LEFT JOIN
            (SELECT t.mail_id_id, eadest.emailadress_id, eadest.firstname, eadest.lastname FROM app1_to t /*Cette sous-requête récupère tout ce qui concerne les destinataires*/
                LEFT JOIN 
                (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
                    LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
                ON t.emailadress_id_id=eadest.emailadress_id 
                ) dest ON m.mail_id=dest.mail_id_id
            WHERE m.path LIKE '/smith-m%' AND dest.emailadress_id='matt.smith@enron.com'
            GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate ;



SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
    LEFT JOIN 
    (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea 
        LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
    ON aut.emailadress_id=m.emailadress_id_id
    LEFT JOIN 
    (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t 
        INNER JOIN app1_emailadress ea2 
            ON t.emailadress_id_id=ea2.emailadress_id 
        GROUP BY t.mail_id_id ) dint 
    ON m.mail_id=dint.mail_id_id
    LEFT JOIN
    (SELECT t.mail_id_id, eadest.emailadress_id, eadest.firstname, eadest.lastname FROM app1_to t 
        LEFT JOIN 
        (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
            LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
        ON t.emailadress_id_id=eadest.emailadress_id ) dest 
    ON m.mail_id=dest.mail_id_id
    WHERE m.path LIKE '/smith-m%'AND dest.emailadress_id = 'matt.smith@enron.com' GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate ;
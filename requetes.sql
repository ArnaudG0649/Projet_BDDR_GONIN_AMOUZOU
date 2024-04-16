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

----par mails envoyés----
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
    WHERE nbmail>100
;

----version où l'on peut filtrer les destinataires internes ou externes (on considérera un échange comme interne quand strictement tous les destinataires sont internes)----

SELECT Ti.lastname, Ti.firstname, (Ti.nbinterne + Te.nbexterne) as nbmail, Ti.nbinterne, Te.nbexterne FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbinterne  FROM /*Cette partie compte le nombre de mails internes envoyés par employé*/
        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id /*On fait une sous-requête pour selectionner tous les employés et leurs adresses*/
            FROM app1_emailadress ea
            INNER JOIN app1_employee emp
                ON emp.employee_id=ea.employee_id_id
        ) emp
        LEFT JOIN 
        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne /*Dans cette sous-requête on associe les mails à leurs destinataires ce qui permet de déduire si l'échange est interne ou interne-externe)*/
                    FROM app1_to t 
                    INNER JOIN app1_emailadress ea2 
                        ON t.emailadress_id_id=ea2.emailadress_id 
                GROUP BY t.mail_id_id
                ) t0
            INNER JOIN app1_mail m /*Ensuite on joint les mails à leur expéditeurs*/
                ON m.mail_id=t0.mail_id_id
            WHERE  t0.interne = True AND m.Timedate > '2001-01-01 00:00:00'
        ) m
            ON m.emailadress_id_id=emp.emailadress_id
        GROUP BY emp.employee_id,emp.lastname,emp.firstname
    )Ti
    INNER JOIN 
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbexterne FROM /*Cette partie est similaire à Ti mais cette fois çi on selectionne que les mails externes*/
        (SELECT emp.lastname,emp.firstname, ea.emailadress_id,emp.employee_id 
            FROM app1_emailadress ea
            INNER JOIN app1_employee emp
                ON emp.employee_id=ea.employee_id_id
        ) emp
        LEFT JOIN 
        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                    FROM app1_to t 
                    INNER JOIN app1_emailadress ea2 
                        ON t.emailadress_id_id=ea2.emailadress_id 
                GROUP BY t.mail_id_id
                ) t0
            INNER JOIN app1_mail m 
                ON m.mail_id=t0.mail_id_id
            WHERE  t0.interne = False AND m.Timedate > '2001-01-01 00:00:00'
        ) m
            ON m.emailadress_id_id=emp.emailadress_id
        GROUP BY emp.employee_id,emp.lastname,emp.firstname
    )Te
    ON Ti.employee_id=Te.employee_id
    WHERE Ti.nbinterne + Te.nbexterne>100
;


----par mails reçus----
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

SELECT Ti.lastname, Ti.firstname, (Ti.nbinterne + Te.nbexterne) as nbmail, Ti.nbinterne, Te.nbexterne FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbinterne /*Cette partie compte le nombre de mails internes reçus par employé*/
    FROM 
        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id /*On fait une sous-requête pour selectionner tous les employés et leurs adresses*/
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        ) emp
    LEFT JOIN 
        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne /*Puis dans cette autre sous requête on selectionne tous leurs mails reçu. Le Left join permet de garder l'employé dans la colonne même s'il n'a pas reçu du mail (cas récurrent lorsqu'il s'agit de mails externes)*/
        FROM app1_to t
        INNER JOIN app1_mail m
            ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2
            ON ea2.emailadress_id=m.emailadress_id_id
        WHERE m.Timedate > '2000-01-01 00:00:00' AND ea2.interne=True
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) Ti
    INNER JOIN 
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbexterne /*Cette partie est similaire à Ti mais cette fois çi on selectionne que les mails externes*/
    FROM 
        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        ) emp
    LEFT JOIN 
        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne
        FROM app1_to t
        INNER JOIN app1_mail m
            ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2
            ON ea2.emailadress_id=m.emailadress_id_id
        WHERE m.Timedate > '2000-01-01 00:00:00' AND ea2.interne=False
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) Te
    ON Ti.employee_id=Te.employee_id
    WHERE Ti.nbinterne + Te.nbexterne>100
;

----Requête n°3----

/*Liste des employés ayant envoyé un mail à tel*/
SELECT emp.firstname, emp.lastname
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND m.Timedate > '2000-01-01 00:00:00' 
    GROUP BY emp.firstname, emp.lastname
;

/*Liste des employés ayant reçu un mail de un tel*/
SELECT emp.firstname, emp.lastname
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND m.Timedate > '2000-01-01 00:00:00' 
    GROUP BY emp.firstname, emp.lastname
;

/*Union des deux*/    
SELECT * FROM (
    SELECT emp.firstname, emp.lastname
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND m.Timedate > '2000-01-01 00:00:00' 
    GROUP BY emp.firstname, emp.lastname
    ) T1
    UNION
SELECT * FROM (
    SELECT emp.firstname, emp.lastname
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND m.Timedate > '2000-01-01 00:00:00' 
    GROUP BY emp.firstname, emp.lastname
    ) T2
;
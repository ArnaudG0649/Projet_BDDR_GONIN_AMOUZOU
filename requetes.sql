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
    WHERE nbmail>10
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
    WHERE nbmail>10
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


----Requête n°4----

SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail /*Cette requête compte le nombre de mails que l'employé de gauche à envoyé à l'employé de droite*/
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
    WHERE m.Timedate > '2000-01-01 00:00:00'
GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname 
;


SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail /*Cette requête compte le nombre de mails que l'employé de droite à envoyé à l'employé de gauche*/
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE m.Timedate > '2000-01-01 00:00:00' 
    GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname
;



(SELECT m.employee_id as id_destinataire, SUM(m.nbmail) as nbmail, ea.employee_id as id_expediteur FROM 
(SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
    INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
) ea
INNER JOIN
(SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
RIGHT JOIN
    (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
    RIGHT JOIN
        (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
            INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
            ON ea2.emailadress_id=t.emailadress_id_id /*les adresses mails des destinataires*/
    ) t ON t.mail_id_id=m.mail_id
GROUP BY t.employee_id, m.emailadress_id_id
) m ON ea.emailadress_id=m.emailadress_id_id
GROUP BY m.employee_id,ea.employee_id
UNION
SELECT c.aid, c.aid*0, c.bid FROM 
    (SELECT a.employee_id as aid, b.employee_id as bid
    FROM app1_employee a CROSS JOIN app1_employee b
    EXCEPT (SELECT mid, eid FROM
        (SELECT m.employee_id as mid, SUM(m.nbmail), ea.employee_id as eid FROM 
        (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
            INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
        ) ea
        INNER JOIN
        (SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
        RIGHT JOIN
            (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
            RIGHT JOIN
                (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                    ON ea2.emailadress_id=t.emailadress_id_id /*les adresses mails des destinataires*/
            ) t ON t.mail_id_id=m.mail_id
        GROUP BY t.employee_id, m.emailadress_id_id
        ) m ON ea.emailadress_id=m.emailadress_id_id
        GROUP BY m.employee_id, ea.employee_id ) ea
    ) ) c )Tdp
;

SELECT Tdp.id_expediteur as employe1, Tdp.id_destinataire as employe2, Tdp.nbmail as nbgauche_droite, Tdp2.nbmail as nbdroite_gauche FROM
    (SELECT m.employee_id as id_destinataire, SUM(m.nbmail) as nbmail, ea.employee_id as id_expediteur FROM 
    (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
    ) ea
    INNER JOIN
    (SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
    RIGHT JOIN
        (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
        RIGHT JOIN
            (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                ON ea2.emailadress_id=t.emailadress_id_id /*les adresses mails des destinataires*/
        ) t ON t.mail_id_id=m.mail_id
    GROUP BY t.employee_id, m.emailadress_id_id
    ) m ON ea.emailadress_id=m.emailadress_id_id
    GROUP BY m.employee_id,ea.employee_id
    UNION
    SELECT c.aid, c.aid*0, c.bid FROM 
        (SELECT a.employee_id as aid, b.employee_id as bid
        FROM app1_employee a CROSS JOIN app1_employee b
        EXCEPT (SELECT mid, eid FROM
            (SELECT m.employee_id as mid, SUM(m.nbmail), ea.employee_id as eid FROM 
            (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
            ) ea
            INNER JOIN
            (SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
            RIGHT JOIN
                (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
                RIGHT JOIN
                    (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                        INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                        ON ea2.emailadress_id=t.emailadress_id_id /*les adresses mails des destinataires*/
                ) t ON t.mail_id_id=m.mail_id
            GROUP BY t.employee_id, m.emailadress_id_id
            ) m ON ea.emailadress_id=m.emailadress_id_id
            GROUP BY m.employee_id, ea.employee_id ) ea
        ) ) c )Tdp
INNER JOIN 
    (SELECT t.employee_id as id_expediteur, SUM(t.nbmail) as nbmail, ea.employee_id as id_destinataire FROM 
    (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
    ) ea
    INNER JOIN
    (SELECT m.employee_id, COUNT(m.mail_id) AS nbmail, t.emailadress_id_id FROM app1_to t 
    RIGHT JOIN
        (SELECT ea2.employee_id, m.mail_id FROM app1_mail m 
        RIGHT JOIN
            (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                ON ea2.emailadress_id=m.emailadress_id_id /*les adresses mails des expediteurs*/
        ) m ON t.mail_id_id=m.mail_id
    GROUP BY m.employee_id, t.emailadress_id_id
    ) t ON ea.emailadress_id=t.emailadress_id_id
    GROUP BY t.employee_id,ea.employee_id
    UNION
    SELECT c.aid, c.aid*0, c.bid FROM 
        (SELECT a.employee_id as aid, b.employee_id as bid
        FROM app1_employee a CROSS JOIN app1_employee b
        EXCEPT (SELECT mid, eid FROM
            (SELECT t.employee_id as mid, SUM(t.nbmail) as nbmail, ea.employee_id as eid FROM 
            (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
            ) ea
            INNER JOIN
            (SELECT m.employee_id, COUNT(m.mail_id) AS nbmail, t.emailadress_id_id FROM app1_to t 
            RIGHT JOIN
                (SELECT ea2.employee_id, m.mail_id FROM app1_mail m 
                RIGHT JOIN
                    (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                        INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                        ON ea2.emailadress_id=m.emailadress_id_id /*les adresses mails des expediteurs*/
                ) m ON t.mail_id_id=m.mail_id
            GROUP BY m.employee_id, t.emailadress_id_id
            ) t ON ea.emailadress_id=t.emailadress_id_id
            GROUP BY t.employee_id,ea.employee_id ) ea
        ) ) c )Tdp2
ON Tdp.id_expediteur=Tdp2.id_destinataire WHERE Tdp.id_destinataire=Tdp2.id_expediteur
GROUP BY employe1, employe2,nbgauche_droite, nbdroite_gauche
ORDER BY nbdroite_gauche DESC
;



SELECT t.employee_id as id_expediteur, SUM(t.nbmail) as nbmail, ea.employee_id as id_destinataire FROM 
(SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
    INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
) ea
INNER JOIN
(SELECT m.employee_id, COUNT(m.mail_id) AS nbmail, t.emailadress_id_id FROM app1_to t 
RIGHT JOIN
    (SELECT ea2.employee_id, m.mail_id FROM app1_mail m 
    RIGHT JOIN
        (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
            INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
            ON ea2.emailadress_id=m.emailadress_id_id /*les adresses mails des expediteurs*/
    ) m ON t.mail_id_id=m.mail_id
GROUP BY m.employee_id, t.emailadress_id_id
) t ON ea.emailadress_id=t.emailadress_id_id
GROUP BY t.employee_id,ea.employee_id
ORDER BY nbmail DESC



SELECT ea2.employee_id FROM app1_mail m 
    RIGHT JOIN
        (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
            INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
            ON ea2.emailadress_id=m.emailadress_id_id 
GROUP BY ea2.employee_id





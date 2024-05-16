----Requête n°4----

/*Cette requête compte le nombre de mails que l'employé de gauche à envoyé à l'employé de droite*/
SELECT * FROM (
SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
    GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname 
    ORDER BY COUNT(m.mail_id) DESC ) T
    WHERE T.nbmail >= 600
;

/*Cette requête compte le nombre de mails que l'employé de droite à envoyé à l'employé de gauche*/
SELECT * FROM (
SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
    GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname
    ORDER BY COUNT(m.mail_id) DESC ) T
    WHERE T.nbmail >= 600       
;


SELECT T.employe1_id, empg.firstname as prenom1, empg.lastname as nom1, T.employe2_id, empd.firstname as prenom2, empd.lastname as nom2, T.nbgauche_droite, T.nbdroite_gauche, T.nbgauche_droite+T.nbdroite_gauche as Total FROM
(SELECT Tdp.id_expediteur as employe1_id, Tdp.id_destinataire as employe2_id, Tdp.nbmail as nbgauche_droite, Tdp2.nbmail as nbdroite_gauche FROM
    (SELECT m.employee_id as id_destinataire, SUM(m.nbmail) as nbmail, ea.employee_id as id_expediteur FROM /*(1) Cette sous-requête donne le nombre de mail que id_destinataire a reçus de id_expediteurs*/
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
    WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
    GROUP BY t.employee_id, m.emailadress_id_id
    ) m ON ea.emailadress_id=m.emailadress_id_id
    GROUP BY m.employee_id,ea.employee_id
    UNION /*On complète la table donnée avec le reste du produit cartésien des employés pour ne pas avoir de case vide lorsqu'on voudra afficher sur la même ligne les mails que l'un à envoyé à l'autre et réciproquement.*/
    SELECT c.aid, c.aid*0, c.bid FROM 
        (SELECT a.employee_id as aid, b.employee_id as bid
        FROM app1_employee a CROSS JOIN app1_employee b
        EXCEPT (SELECT mid, eid FROM 
            (SELECT m.employee_id as mid, SUM(m.nbmail), ea.employee_id as eid FROM /*On refait exactement la requête (1) (jusqu'au UNION)*/
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
            WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
            GROUP BY t.employee_id, m.emailadress_id_id
            ) m ON ea.emailadress_id=m.emailadress_id_id
            GROUP BY m.employee_id, ea.employee_id ) ea
        ) ) c )Tdp
INNER JOIN /*Ensuite on refait la même chose en échangeant expediteurs et destinataires pour avoir les nombres de mails envoyés dans l'autre sens (Tdp2.nbmail)*/
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
                ON ea2.emailadress_id=m.emailadress_id_id 
                WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
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
                        ON ea2.emailadress_id=m.emailadress_id_id 
                        WHERE ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
                ) m ON t.mail_id_id=m.mail_id
            GROUP BY m.employee_id, t.emailadress_id_id
            ) t ON ea.emailadress_id=t.emailadress_id_id
            GROUP BY t.employee_id,ea.employee_id ) ea
        ) ) c )Tdp2
ON Tdp.id_expediteur=Tdp2.id_destinataire WHERE Tdp.id_destinataire=Tdp2.id_expediteur
GROUP BY employe1_id, employe2_id, nbgauche_droite, nbdroite_gauche ) T
INNER JOIN app1_employee empg ON empg.employee_id=T.employe1_id /*Ces deux jointures ont pour seul but de récupérer les noms et prénoms des employés à la fin*/
INNER JOIN app1_employee empd ON empd.employee_id=T.employe2_id
WHERE T.nbgauche_droite + T.nbdroite_gauche >= 0
ORDER BY T.nbgauche_droite+T.nbdroite_gauche DESC
;

----Version où l'on ne garde qu'un seul employé à gauche----

/*Tous les mails que Kevin Presto a reçus*/
SELECT * FROM(
SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nb FROM 
    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
       ) emp
    LEFT JOIN 
        (SELECT m.emailadress_id_id, m.mail_id
        FROM app1_mail m
        INNER JOIN app1_to t ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2 ON t.emailadress_id_id=ea2.emailadress_id
        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
        ) m
        ON m.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ORDER BY nb DESC) T
WHERE T.nb >= 100    

/*Tous les mails que Kevin Presto a envoyés*/
SELECT * FROM(
SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nb FROM 
    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
       ) emp
    LEFT JOIN 
        (SELECT t.emailadress_id_id, m.mail_id
        FROM app1_to t
        INNER JOIN app1_mail m ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2 ON m.emailadress_id_id=ea2.emailadress_id
        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ORDER BY nb DESC) T
WHERE T.nb >= 100

----Mails que Kevin Preston a reçus et envoyés----
SELECT ENV.lastname, ENV.Firstname, nbenv, nbrec, nbenv+nbrec as total FROM  
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbenv FROM /*Tous les mails que Kevin Presto a envoyés*/
    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
       ) emp
    LEFT JOIN 
        (SELECT t.emailadress_id_id, m.mail_id
        FROM app1_to t
        INNER JOIN app1_mail m ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2 ON m.emailadress_id_id=ea2.emailadress_id
        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) ENV
INNER JOIN 
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbrec FROM /*Tous les mails que Kevin Presto a reçus*/
    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
       ) emp
    LEFT JOIN 
        (SELECT m.emailadress_id_id, m.mail_id
        FROM app1_mail m
        INNER JOIN app1_to t ON m.mail_id = t.mail_id_id
        INNER JOIN app1_emailadress ea2 ON t.emailadress_id_id=ea2.emailadress_id
        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
        ) m
        ON m.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) REC
    ON ENV.employee_id = REC.employee_id
    WHERE nbenv+nbrec >= 100
    ORDER BY total DESC 

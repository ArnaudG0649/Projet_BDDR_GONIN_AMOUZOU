----Requête n°1----
SELECT *
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE e.lastname='Taylor' AND e.firstname='Mark'
;


SELECT e.employee_id, e.lastname, e.firstname, e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ') /*Version où l'on concatène les adresses mails*/
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE e.lastname='Taylor' AND e.firstname='Mark'
GROUP BY e.employee_id, e.lastname, e.firstname, e.category, e.mailbox
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


SELECT e.firstname , e.lastname , e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ') /*Version où l'on concatène les adresses mails*/
FROM (SELECT * /*Cette sous-requête a pour but de récupérer l'id de l'employé à partir de l'adresse mail*/
    FROM app1_employee e
    INNER JOIN app1_emailadress ea
        ON e.employee_id=ea.employee_id_id
    WHERE ea.emailadress_id='elizabeth.sager@enron.com') e
INNER JOIN app1_emailadress ea /*Puis ce join permet de récupérer toutes ces autres adresses mails*/
    ON e.employee_id=ea.employee_id_id
GROUP BY e.firstname, e.lastname , e.category, e.mailbox
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
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00')
    GROUP BY emp.firstname, emp.lastname
    ORDER BY lastname
;

/*Liste des employés ayant reçu un mail de un tel*/
SELECT emp.firstname, emp.lastname
    FROM app1_employee emp
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00') 
    GROUP BY emp.firstname, emp.lastname
    ORDER BY lastname
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
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00' ) 
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
        WHERE emp2.lastname='Presto' AND emp2.firstname='Kevin' AND ( m.Timedate BETWEEN '2000-01-01 00:00:00' AND '2100-01-01 00:00:00') 
    GROUP BY emp.firstname, emp.lastname
    ) T2
    ORDER BY lastname
;


----Requête n°4----
SELECT * FROM (
SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail /*Cette requête compte le nombre de mails que l'employé de gauche à envoyé à l'employé de droite*/
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

SELECT * FROM (
SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail /*Cette requête compte le nombre de mails que l'employé de droite à envoyé à l'employé de gauche*/
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

----Requête n°5----

/* SELECT COUNT(mail_id) FROM */

SELECT COUNT(T.mail_id) FROM (
SELECT m.mail_id, m.subject, m.emailadress_id_id, t.dest_interne, aut.interne as exp_interne FROM app1_mail m 
    INNER JOIN 
    (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
    INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
    GROUP BY t.mail_id_id
    ) t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
    WHERE (m.Timedate BETWEEN '2001-10-01 00:00:00' AND '2001-10-02 00:00:00') AND ((aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True)) /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
) T
;

SELECT COUNT(T.mail_id) FROM (
SELECT m.mail_id, m.subject, m.emailadress_id_id, t.dest_interne, aut.interne as exp_interne FROM app1_mail m 
    INNER JOIN 
    (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
    INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
    GROUP BY t.mail_id_id
    ) t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
    WHERE (m.Timedate BETWEEN '2001-10-01 00:00:00' AND '2001-10-02 00:00:00') AND (aut.interne=True AND t.dest_interne=True) 
) T
;



----Requête n°6----

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
    WHERE m.Timedate > '2000-01-01' AND dest.firstname='Jeff' AND dest.lastname='King' AND aut.interne=False /*Ensuite on filtre ce qu'on veut*/
GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate 
;
        
                









    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
    INNER JOIN app1_emailadress eadest ON eadest.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
    WHERE m.Timedate > '2001-01-01' AND t.emailadress_id_id='laurie.ellis@enron.com' AND aut.interne=True 
GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate
;
/*!! Ne pas faire d'inner join inutile sinon ça supprime les mails nécessaires de la table*/

SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
    WHERE m.mail_id='711760.1075858202707.JavaMail.evans@thyme'
;








----Requête n°7----

/*On considérera une discussion comme l'ensemble des mails que deux employés se sont échangés, éventuellement restreint à une période donnée.*/
SELECT T.mail_id, T.subject, T.path, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur FROM
(SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    WHERE emp.firstname='Patrice' AND emp.lastname='Mims') empexp 
    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
    INNER JOIN
    (SELECT ea.emailadress_id FROM app1_employee emp 
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    WHERE emp.firstname='Debra' AND emp.lastname='Perlingiere') empdest ON empdest.emailadress_id=t.emailadress_id_id
UNION
SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    WHERE emp.firstname='Debra' AND emp.lastname='Perlingiere') empexp 
    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
    INNER JOIN
    (SELECT ea.emailadress_id FROM app1_employee emp 
    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
    WHERE emp.firstname='Patrice' AND emp.lastname='Mims') empdest ON empdest.emailadress_id=t.emailadress_id_id
) T
WHERE T.Timedate > '2001-10-01 00:00:00'
ORDER BY Timedate 
;

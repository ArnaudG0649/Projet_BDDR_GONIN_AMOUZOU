----Requête n°1----
SELECT *
FROM app1_employee e
INNER JOIN app1_emailadress ea
    ON e.employee_id=ea.employee_id_id
WHERE e.lastname='Taylor' AND e.firstname='Mark'
;

/*Version où l'on concatène les adresses mails*/
SELECT e.employee_id, e.lastname, e.firstname, e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ') 
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

/*Version où l'on concatène les adresses mails*/
SELECT e.firstname , e.lastname , e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ') 
FROM (SELECT * /*Cette sous-requête a pour but de récupérer l'id de l'employé à partir de l'adresse mail*/
    FROM app1_employee e
    INNER JOIN app1_emailadress ea
        ON e.employee_id=ea.employee_id_id
    WHERE ea.emailadress_id='elizabeth.sager@enron.com') e
INNER JOIN app1_emailadress ea /*Puis ce join permet de récupérer toutes ces autres adresses mails*/
    ON e.employee_id=ea.employee_id_id
GROUP BY e.firstname, e.lastname , e.category, e.mailbox
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


----Requête n°5----

SELECT * FROM (
    SELECT COUNT(T.mail_id) as nb, T.date FROM (
    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
        LEFT JOIN /*Ce LEFT JOIN a pour but de compter "0" les jours où il n'y a pas de mails correspondant à la condition sur les internes ou les externes*/
        (SELECT m.mail_id, m.timedate FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
    GROUP BY T.date ) T2
WHERE T2.date BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
ORDER BY T2.nb DESC
;

SELECT * FROM (
    SELECT COUNT(T.mail_id) as nb, T.date FROM (
    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
        LEFT JOIN
        (SELECT m.mail_id, m.timedate FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
    GROUP BY T.date ) T2
WHERE T2.date BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
ORDER BY T2.nb DESC
;

/*Deux cas*/
SELECT INT_EXT.date, INT_EXT.nbint_ext as nbint_ext, INT_INT.nbint_int as nbint_int, INT_EXT.nbint_ext + INT_INT.nbint_int as Total FROM (
SELECT COUNT(T.mail_id) as nbint_ext, T.date FROM (
    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
        LEFT JOIN
        (SELECT m.mail_id, m.timedate FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T
    GROUP BY T.date ) INT_EXT
INNER JOIN (
SELECT COUNT(T.mail_id) as nbint_int, T.date FROM (
    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
        LEFT JOIN
        (SELECT m.mail_id, m.timedate FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
GROUP BY T.date ) INT_INT ON INT_INT.date = INT_EXT.date
WHERE INT_EXT.date BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
ORDER BY INT_EXT.nbint_ext + INT_INT.nbint_int DESC
;


----Requête n°6----
        
SELECT max(m.path) as path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
    LEFT JOIN 
    (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea /*Cette sous-requête récupère tout ce qui concerne les auteurs*/
        LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
    ON aut.emailadress_id=m.emailadress_id_id
    LEFT JOIN 
    (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t /*Cette sous-requête permet de dire si un mail a été envoyé qu'à des destinataires internes ou s'il y a un destinataires externe dans le mail*/
        INNER JOIN app1_emailadress ea2 
            ON t.emailadress_id_id=ea2.emailadress_id 
        GROUP BY t.mail_id_id ) dint 
    ON m.mail_id=dint.mail_id_id
    LEFT JOIN
    (SELECT t.mail_id_id, eadest.emailadress_id, eadest.firstname, eadest.lastname FROM app1_to t /*Cette sous-requête récupère tout ce qui concerne les destinataires*/
        LEFT JOIN 
        (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
            LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
        ON t.emailadress_id_id=eadest.emailadress_id ) dest 
    ON m.mail_id=dest.mail_id_id
    LEFT JOIN 
    (SELECT c.mail_id_id, bool_and(ea2.interne) as interne FROM app1_cc c /*Cette sous-requête permet de dire si un mail a été mis en copie qu'à des adresses internes ou s'il y a une adresse externe dans le mail*/
        INNER JOIN app1_emailadress ea2 
            ON c.emailadress_id_id=ea2.emailadress_id 
        GROUP BY c.mail_id_id ) cint 
    ON m.mail_id=cint.mail_id_id
    LEFT JOIN
    (SELECT c.mail_id_id, eacc.emailadress_id, eacc.firstname, eacc.lastname FROM app1_cc c /*Cette sous-requête récupère tout ce qui concerne les destinataires*/
        LEFT JOIN 
        (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
            LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eacc
        ON c.emailadress_id_id=eacc.emailadress_id ) cc 
    ON m.mail_id=cc.mail_id_id
    WHERE m.Timedate > '2000-01-01' AND cc.firstname='Jeff' AND cc.lastname='King' AND cint.interne=True /*Ensuite on filtre ce qu'on veut*/
GROUP BY m.emailadress_id_id, m.subject, m.timedate
ORDER BY m.timedate 
;


----Requête n°7----

/*On considérera une conversation comme l'ensemble des mails que deux employés se sont échangés, éventuellement restreint à une période donnée.*/
SELECT T.subject, max(T.path) as path, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur FROM
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
WHERE T.Timedate > '2001-01-01 00:00:00'
GROUP BY T.subject, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur
ORDER BY T.Timedate 
;

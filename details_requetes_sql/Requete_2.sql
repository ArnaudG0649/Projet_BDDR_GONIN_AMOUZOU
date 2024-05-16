----Requête n°2----

----par mails envoyés----
SELECT lastname,firstname,nbmail FROM
    (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail   
        FROM app1_emailadress ea
        INNER JOIN app1_employee emp
            ON emp.employee_id=ea.employee_id_id
        INNER JOIN app1_mail m 
            ON m.emailadress_id_id=ea.emailadress_id
        WHERE Timedate BETWEEN '2001-01-25 04:20' AND '2100-01-01 00:00:00'
        GROUP BY emp.employee_id
    ) T
    WHERE nbmail >= 100
    ORDER BY nbmail DESC
;

----version où l'on peut filtrer les destinataires internes ou externes (on considérera un échange comme interne quand strictement tous les destinataires sont internes)----

SELECT Ti.lastname, Ti.firstname, Ti.nbinterne, Te.nbexterne, (Ti.nbinterne + Te.nbexterne) as nbmail FROM
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
            WHERE  t0.interne = True AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
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
            WHERE  t0.interne = False AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
        ) m
            ON m.emailadress_id_id=emp.emailadress_id
        GROUP BY emp.employee_id,emp.lastname,emp.firstname
    )Te
    ON Ti.employee_id=Te.employee_id
    WHERE Ti.nbinterne + Te.nbexterne >= 100
    ORDER BY Ti.nbinterne + Te.nbexterne DESC
;


----Mails internes envoyés----
SELECT T.lastname, T.firstname, T.nb FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nb FROM 
            (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
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
                WHERE  t0.interne = True AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
            ) m
                ON m.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id,emp.lastname,emp.firstname) T
    WHERE nb >= 100
    ORDER BY nb DESC
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
        WHERE Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
        GROUP BY emp.employee_id
    ) T
    WHERE nbmail >= 100
    ORDER BY nbmail DESC
;

----version où l'on peut filtrer les expéditeurs internes ou externes---- 

SELECT Ti.lastname, Ti.firstname, Ti.nbinterne, Te.nbexterne, (Ti.nbinterne + Te.nbexterne) as nbmail FROM
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
        WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=True
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
        WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=False
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) Te
    ON Ti.employee_id=Te.employee_id
    WHERE Ti.nbinterne + Te.nbexterne>100
    ORDER BY Ti.nbinterne + Te.nbexterne DESC
; 


----Mails internes reçus----
SELECT Ti.lastname, Ti.firstname, Ti.nb FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nb 
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
        WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=True
        ) t
        ON t.emailadress_id_id=emp.emailadress_id
    GROUP BY emp.employee_id, emp.lastname, emp.firstname
    ) Ti
    WHERE Ti.nb >= 100
    ORDER BY nb DESC
;


----Mails envoyés et reçus----

SELECT Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv AS total FROM
    (SELECT emp.employee_id, emp.lastname,emp.firstname, COUNT(m.mail_id) as nbenv   
        FROM app1_employee emp
        INNER JOIN app1_emailadress ea 
            ON emp.employee_id=ea.employee_id_id
        LEFT JOIN (SELECT emailadress_id_id, mail_id FROM app1_mail WHERE Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' ) m
            ON m.emailadress_id_id=ea.emailadress_id
        GROUP BY emp.employee_id, emp.lastname,emp.firstname
    ) Env
INNER JOIN 
    (SELECT emp.employee_id, emp.lastname,emp.firstname, COUNT(t.mail_id_id) as nbrec  
        FROM app1_employee emp
        INNER JOIN app1_emailadress ea 
            ON emp.employee_id=ea.employee_id_id
        LEFT JOIN 
        (SELECT t.mail_id_id, t.emailadress_id_id FROM app1_to t
            LEFT JOIN app1_mail m ON t.mail_id_id=m.mail_id
            WHERE Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
         ) t
            ON t.emailadress_id_id=ea.emailadress_id
        GROUP BY emp.employee_id, emp.lastname,emp.firstname
    ) Rec
    ON Env.employee_id=Rec.employee_id
    WHERE Rec.nbrec+Env.nbenv >= 100
    ORDER BY Rec.nbrec+Env.nbenv DESC
;


----Mails internes envoyés et reçu----

SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv as total FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM /*Cette partie compte le nombre de mails internes envoyés par employé*/
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
                WHERE  t0.interne = True AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
            ) m
                ON m.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id,emp.lastname,emp.firstname
        ) Env
    INNER JOIN
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec /*Cette partie compte le nombre de mails internes reçus par employé*/
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
            WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=True
            ) t
            ON t.emailadress_id_id=emp.emailadress_id
        GROUP BY emp.employee_id, emp.lastname, emp.firstname
        ) Rec
    ON Env.employee_id=Rec.employee_id
    WHERE Rec.nbrec+Env.nbenv >= 100
    ORDER BY Rec.nbrec+Env.nbenv DESC;




----Mails externes envoyés et reçu----
SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv as total FROM
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM /*Cette partie compte le nombre de mails internes envoyés par employé*/
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
                WHERE  t0.interne = False AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
            ) m
                ON m.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id,emp.lastname,emp.firstname
        ) Env
    INNER JOIN
    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec /*Cette partie compte le nombre de mails internes reçus par employé*/
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
            WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=False
            ) t
            ON t.emailadress_id_id=emp.emailadress_id
        GROUP BY emp.employee_id, emp.lastname, emp.firstname
        ) Rec
    ON Env.employee_id=Rec.employee_id
    WHERE Rec.nbrec+Env.nbenv >= 100
    ORDER BY Rec.nbrec+Env.nbenv DESC;

----Tout----

SELECT INTE.employee_id, INTE.lastname, INTE.firstname, INTE.nbenvint, INTE.nbrecint, EXT.nbenvext, EXT.nbrecext, INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext as total FROM
    (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvint, Rec.nbrec as nbrecint FROM
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM /*Cette partie compte le nombre de mails internes envoyés par employé*/
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
                    WHERE  t0.interne = True AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
                ) m
                    ON m.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id,emp.lastname,emp.firstname
            ) Env
        INNER JOIN
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec /*Cette partie compte le nombre de mails internes reçus par employé*/
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
                WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=True
                ) t
                ON t.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id, emp.lastname, emp.firstname
            ) Rec
        ON Env.employee_id=Rec.employee_id ) INTE
    INNER JOIN 
    (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvext, Rec.nbrec as nbrecext FROM
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM /*Cette partie compte le nombre de mails internes envoyés par employé*/
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
                    WHERE  t0.interne = False AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
                ) m
                    ON m.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id,emp.lastname,emp.firstname
            ) Env
        INNER JOIN
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec /*Cette partie compte le nombre de mails internes reçus par employé*/
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
                WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=False
                ) t
                ON t.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id, emp.lastname, emp.firstname
            ) Rec
        ON Env.employee_id=Rec.employee_id) EXT
    ON INTE.employee_id=EXT.employee_id
    WHERE INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext >= 1000
    ORDER BY total DESC;




----Idem sauf que le résultat final ne détail pas le nombre de mails envoyés et reçus.---- 

SELECT INTE.lastname, INTE.firstname, INTE.nbenvint + INTE.nbrecint as nbint, EXT.nbenvext + EXT.nbrecext as nbext, INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext as total FROM
    (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvint, Rec.nbrec as nbrecint FROM
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
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
                    WHERE  t0.interne = True AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
                ) m
                    ON m.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id,emp.lastname,emp.firstname
            ) Env
        INNER JOIN
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
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
                WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=True
                ) t
                ON t.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id, emp.lastname, emp.firstname
            ) Rec
        ON Env.employee_id=Rec.employee_id ) INTE
    INNER JOIN 
    (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvext, Rec.nbrec as nbrecext FROM
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
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
                    WHERE  t0.interne = False AND m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00'
                ) m
                    ON m.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id,emp.lastname,emp.firstname
            ) Env
        INNER JOIN
        (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
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
                WHERE m.Timedate BETWEEN '2001-01-01 00:00:00' AND '2100-01-01 00:00:00' AND ea2.interne=False
                ) t
                ON t.emailadress_id_id=emp.emailadress_id
            GROUP BY emp.employee_id, emp.lastname, emp.firstname
            ) Rec
        ON Env.employee_id=Rec.employee_id) EXT
    ON INTE.employee_id=EXT.employee_id
    WHERE INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext >= 1000
    ORDER BY total DESC;
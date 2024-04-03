Le fichier "projetenron" est le ficher d'un projet Django avec lequel on crée et on peuple les tables qui contiendront les données nécessaires aux requêtes demandées. L'application web sera aussi faite à partir de ce projet.
Après avoir créé les tables définies dans le fichier models du répertoire app1, pour peupler la base de donnée il suffit de placer le dossier des mails maildir dans le dossier projetenron (c'est-à-dire avoir Projet_BDDR_GONIN_AMOUZOU/projetenron/maildir) et d'executer le fichier Script_Peuplement.py.
Pour l'instant, le peuplement de la table "RE" est mise à l'écart. En effet, cette table contient deux colonnes :
-La clé primaire remail_id qui est l'id d'un mail "réponse".
-La colonne mail_id qui est le mail "répondu".
La création de cette table nécessite de pouvoir identifier dans un mail dont le sujet commence par "RE:" quel est le mail répondu. Or faire cela pose beaucoup de problèmes comme :
-L'absence de l'id du mail répondu
-Les noms des utilisateurs à la place de leurs adresses mail dans la partie "-----Original Message-----"
-Les dates et heures incomplètes dans cette même partie
-Et surtout on a eu un problème important avec un test. Après avoir fait un test avec le mail 9. (vous pouvez le voir juste ici : Projet_BDDR_GONIN_AMOUZOU/9.), en cherchant tous les mails dont le sujet était "Lets get this ball rolling...." pour trouver son mail dont il est la réponse, le seul résultat est le mail 39. Alors qu'on retrouve certaines adresses en commun et des dates pas trop éloignées, le texte en dessous de "-----Original Message-----" dans le mail 9. et le contenu du mail 39. sont totalement différents, avec des dates différentes et des destinataires différents. On s'est dit alors qu'il y avait la possibilité que des mails "répondus" ne soit pas dans la base de données, ce qui rend la création de la table "RE" impossible.
Nous n'abandonnons pas définitivement la création de cette table mais nous chercherons surement d'abord à faire toutes les requêtes avant et nous retournerons sur sa création plus tard si c'est vraiment nécessaire, sinon nous risquons de perdre trop de temps alors que, avec du recul, on doute sur sa réel nécessité.

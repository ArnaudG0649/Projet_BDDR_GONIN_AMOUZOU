####INSTALLATION####
1.Assurez-vous qu'il y ait bien tous les dossiers de l'application, et que python3, postgresql et django soient installés sur votre machine.

2.Dans le fichier /projetenron/projetenron/settings.py, entre les lignes 78 et 87 :
-À " 'NAME': 'agonin', ", remplacez agonin par le nom de votre base de données postgresql
-À " 'USER': 'agonin', ", remplacez agonin par votre nom d'utilisateur postgresql
-À " 'PASSWORD': 'agonin', ", remplacez agonin par votre mot de passe postgresql
-À " 'HOST': 'data', ", remplacez data par le nom de votre serveur (souvent c'est 'localhost')
-À " 'PORT': '5432', ", remplacez éventuellement 5432 par le port de votre serveur.

3.Ouvrez un terminal dans le répertoire /projetenron (et pas /projetenron/projetenron), et exécutez à la suite les commandes suivantes :
python manage.py migrate
python manage.py makemigrations app1
python manage.py migrate

4.Assurez-vous que le dossier maildir soit rempli et si c'est ne pas le cas remplissez-le de sorte qu'il soit complétement identique à celui téléchargeable à ce lien (après l'avoir dézippé) :
https://math.univ-angers.fr/perso/jaclin/enron/enron_mail_20150507.tar.gz

5.Lancez la commande " ./Script_Peuplement.py " dans le terminal. Cela peuplera la base de données à partir des mails présents dans le dossier maildir et des informations des employés issus du fichier employes_enron.xml.

6.Quand c'est terminé vous pouvez lancer l'application en exécutant la commande " python manage.py runserver 7000 " puis en ouvrant le lien http://127.0.0.1:7000/Application_Projet/ .
Si ce lien ne marche pas, remplacez la partie http://127.0.0.1:7000 par le lien affiché dans le terminal.

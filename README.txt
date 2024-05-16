####INSTALLATION####
1.Assurez-vous qu'il y ait bien tous les dossiers de l'application.
2.Ouvrez un terminal dans le répertoire /projetenron (et pas /projetenron/projetenron), et exécutez à la suite les commandes suivantes :
python manage.py migrate
python manage.py makemigrations app1
python manage.py migrate
3.Assurez-vous que le dossier maildir soit rempli et si c'est ne pas le cas remplissez-le de sorte qu'il soit complétement identique à celui téléchargeable à ce lien (après l'avoir dézippé) :
https://math.univ-angers.fr/perso/jaclin/enron/enron_mail_20150507.tar.gz
4.Lancez la commande " ./Script_Peuplement.py " dans le terminal. Cela peuplera la base de données à partir des mails présents dans le dossier maildir et des informations des employés issus du fichier employes_enron.xml.
5.Quand c'est terminé vous pouvez lancer l'application en exécutant la commande " python manage.py runserver 7000 " puis en ouvrant le lien http://127.0.0.1:7000/Application_Projet/ .
Si ce lien ne marche pas, remplacez la partie http://127.0.0.1:7000 par le lien affiché dans le terminal.

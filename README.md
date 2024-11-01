# Odoo 18 Leitner system implementation

This project is:

- An example for Odoo 18 addon development.
- An implementation of the Leitner card based learning method.

You will find the addons in the addons directory. The rest of the
project is just a convenient way of launching the whole Odoo
environment using just docker-compose.

## Run oddoo and install the addon

Run the following commands to clean, redeploy and run the application

``` bash
# format the source code, not required for deployment
./scripts/black-and-pretty $PWD/addons
# clean any older deployments
sudo docker-compose down -v
# boot up postgres
sudo docker-compose up -d db
# install addon on new database with demo data
sudo docker-compose run --rm -T odoo odoo --stop-after-init --no-http -d odoodb -i leitner
# boot Odoo
sudo docker-compose up -d
# show logs
sudo docker-compose logs -f odoo
```

A variation you can use after editing the addon:

``` bash
# format the source code
./scripts/black-and-pretty $PWD/addons
# stop odoo, update the addon, restart
sudo docker-compose stop odoo
sudo docker-compose run --rm -T odoo odoo --stop-after-init --no-http -d odoodb -u leitner
sudo docker-compose start odoo
# show logs
sudo docker-compose logs -f odoo
```

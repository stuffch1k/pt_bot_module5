# FROM postgres:16


# ADD db/init.sql /docker-entrypoint-initdb.d/
# COPY .env /.env


# # ARG DB_USER
# # ARG DB_PASSWORD

# # RUN sed -i "s/DB_USER/$DB_USER/g" /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i "s/DB_PASSWORD/$DB_PASSWORD/g" /docker-entrypoint-initdb.d/init.sql

# # RUN sed -i 's/\${DB_USER}/'"$(cat /.env | grep DB_USER | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/${DB_PASSWORD}/(cat /.env | grep DB_USER | cut -d '=' -f2)/g' example.txt

# # RUN sed -i 's/\${DB_PASSWORD}/'"$(cat /.env | grep DB_PASSWORD | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/DB_USER/\$\{$&\}/g'  /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i "s/ALTER ROLE \${DB_USER} PASSWORD '\${DB_PASSWORD}' ;/ALTER ROLE $(cat .env | grep DB_USER | cut -d '=' -f2 | tr -d '\n\r') PASSWORD '$(cat .env | grep DB_PASSWORD | cut -d '=' -f2 | tr -d '\n\r')' ;/" /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/\${DB_USER}/'"$(cat /.env | grep DB_USER | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/\${DB_DATABASE}/'"$(cat /.env | grep DB_DATABASE | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/\${DB_REPL_USER}/'"$(cat /.env | grep DB_REPL_USER | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql
# # RUN sed -i 's/\${DB_REPL_PASSWORD}/'"$(cat /.env | grep DB_REPL_PASSWORD | cut -d '=' -f2)"'/g' /docker-entrypoint-initdb.d/init.sql



# RUN echo "host all all all password" >> pg_hba.conf
# RUN echo "listen_addresses = '*'" >> postgresql.conf


# # RUN echo 'Qq12345' | passwd --stdin postgres 

# RUN chown postgres /docker-entrypoint-initdb.d/init.sql
# RUN su - postgres
# RUN chmod +x  /docker-entrypoint-initdb.d/init.sql


FROM postgres:15.6
RUN mkdir -p /var/log/postgres/ && chown postgres:postgres /var/log/postgresql/ 
RUN touch /var/log/postgres/postgresql.log && chown postgres:postgres /var/log/postgres/postgresql.log && chmod -R 777 /var/log/postgresql/
RUN mkdir -p /oracle/pg_data/archive/ && chown postgres:postgres /oracle/pg_data/archive/
COPY init.sql /docker-entrypoint-initdb.d/
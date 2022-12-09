# useful for handling different item types with a single interface
import pg8000
import json
import logging
import os

class PostgresPipeline(object):
    # Init 
    user            =   os.environ.get('DB_USER' ,'')
    password        =   os.environ.get('DB_PASSWORD', '')
    host            =   os.environ.get('DB_HOSTNAME', '')
    database        =   os.environ.get('DB_DATABASE', '')
    port            =   os.environ.get('DB_PORT', '')
    schema          =   os.environ.get('DB_SCHEMA', '')
    insert_table    =   os.environ.get('DB_INSERT_TABLE', '')
    
    def open_spider(self, spider):
        self.client = pg8000.connect(
                            user=self.user,
                            password = self.password,
                            host = self.host,
                            database = self.database,
                            port = self.port)
        self.curr = self.client.cursor()

    def close_spider(self, spider):
       self.client.close()

    def process_item(self, item, spider):
        # Create table to insert
        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS {schema}.{insert_table} (
                crawl_date timestamp,
                crawl_ts integer,
                gold_code text,
                buying_price integer,
                selling_price integer,
                buy_change integer,
                sell_change integer,
                buy_change_percent decimal,
                sell_change_percent decimal,
                last_update timestamp,
                last_update_ts integer,
                PRIMARY KEY (gold_code, last_update_ts)
            )
        """.format(schema=self.schema, insert_table=self.insert_table)
        )

        self.curr.execute("""
                        INSERT INTO {schema}.{insert_table} VALUES (
                                                                    '{crawlDate}', 
                                                                    '{crawlTimeStamp}',
                                                                    '{goldCode}', 
                                                                    '{buyingPrice}', 
                                                                    '{sellingPrice}', 
                                                                    '{buyChange}', 
                                                                    '{sellChange}', 
                                                                    '{buyChangePercent}', 
                                                                    '{sellChangePercent}', 
                                                                    '{lastUpdate}', 
                                                                    '{lastUpdateTimeStamp}'
                                                                )
                        ON CONFLICT (gold_code, last_update_ts)
                        DO UPDATE
                        SET 
                            crawl_date = excluded.crawl_date,
                            crawl_ts = excluded.crawl_ts,
                            buying_price = excluded.buying_price,
                            selling_price = excluded.selling_price,
                            buy_change = excluded.buy_change,
                            sell_change = excluded.sell_change,
                            buy_change_percent = excluded.buy_change_percent,
                            sell_change_percent = excluded.sell_change_percent,
                            last_update = excluded.last_update
                        """.format(schema=self.schema, insert_table=self.insert_table, **item)
        )
        self.client.commit()
        logging.info("Upserted a record to the table '{schema}.{insert_table}'".format(schema=self.schema, insert_table=self.insert_table))
        return item

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 12:50:03 2021
"""

CREATE TABLE IF NOT EXISTS conversions (
                                    conv_id text NOT NULL,
                                    user_id text NOT NULL,
                                    conv_date text NOT NULL,
                                    conv_time text NOT NULL,
                                    revenue real NOT NULL,
                                    PRIMARY KEY(conv_id)
                                );


CREATE TABLE IF NOT EXISTS session_costs (
                                    session_id text NOT NULL,
                                    cost real,
                                    PRIMARY KEY(session_id)
                                );

CREATE TABLE IF NOT EXISTS session_sources (
                                    session_id text NOT NULL,
                                    user_id text NOT NULL,
                                    event_date text NOT NULL,
                                    event_time text NOT NULL,
                                    channel_name text NOT NULL,
                                    holder_engagement INTEGER NOT NULL,
                                    closer_engagement INTEGER NOT NULL,
                                    impression_interaction INTEGER NOT NULL,
                                    PRIMARY KEY(session_id)
                                );

CREATE TABLE IF NOT EXISTS attribution_customer_journey (
                                    conv_id text NOT NULL,
                                    session_id text NOT NULL,
                                    ihc real NOT NULL,
                                    PRIMARY KEY(conv_id,session_id)
                                );
                                
CREATE TABLE IF NOT EXISTS channel_reporting (
                            channel_name text NOT NULL,
                            date text NOT NULL,
                            cost real NOT NULL,
                            ihc real NOT NULL,
                            ihc_revenue real NOT NULL,
                            PRIMARY KEY(channel_name,date)
                        );

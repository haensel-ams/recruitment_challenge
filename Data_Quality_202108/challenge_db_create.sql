# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 12:50:03 2021
"""

CREATE TABLE IF NOT EXISTS conversions (
                                    conv_id text NOT NULL,
                                    user_id text NOT NULL,
                                    conv_date text NOT NULL,
                                    market text NOT NULL,
                                    revenue real NOT NULL,
                                    PRIMARY KEY(conv_id,user_id,conv_date)
                                );

CREATE TABLE IF NOT EXISTS conversions_backend (
                                    conv_id text NOT NULL,
                                    user_id text NOT NULL,
                                    conv_date text NOT NULL,
                                    market text NOT NULL,
                                    revenue real NOT NULL,
                                    PRIMARY KEY(conv_id,user_id,conv_date)
                                );

CREATE TABLE IF NOT EXISTS api_adwords_costs (
                                    event_date text NOT NULL,
                                    campaign_id text NOT NULL,
                                    cost real NOT NULL,
                                    clicks integer NOT NULL,
                                    PRIMARY KEY(event_date,campaign_id)
                                );

CREATE TABLE IF NOT EXISTS session_sources (
                                    session_id text NOT NULL,
                                    user_id text NOT NULL,
                                    event_date text NOT NULL,
                                    event_time text NOT NULL,
                                    channel_name text NOT NULL,
                                    campaign_name text NOT NULL,
                                    campaign_id text NOT NULL,
                                    market text NOT NULL,
                                    cpc real NOT NULL,
                                    PRIMARY KEY(session_id,user_id,event_date)
                                );

CREATE TABLE IF NOT EXISTS attribution_customer_journey (
                                    conv_id text NOT NULL,
                                    session_id text NOT NULL,
                                    ihc real NOT NULL,
                                    PRIMARY KEY(conv_id,session_id)
                                );
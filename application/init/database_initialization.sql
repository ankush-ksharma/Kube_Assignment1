CREATE TABLE IF NOT EXISTS NAGAP_USER_INFO(
    id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(100) NOT NULL,
    technology_band VARCHAR(100) NOT NULL,
    status VARCHAR(100) NOT NULL
);


INSERT INTO NAGAP_USER_INFO (candidate_name, technology_band, status) VALUES
('User1', 'TechnologyBand1', 'PotentailNAGP'),
('User2', 'TechnologyBand1', 'TaggedNAGAP'),
('User3', 'QABand1', 'PotentailNAGP'),
('User4', 'QABand1', 'TaggedNAGAP'),
('User5', 'ITBand1', 'PotentailNAGP'),
('User6', 'ITBand2', 'TaggedNAGAP'),
('User7', 'DEVOPSBand1', 'PotentailNAGP'),
('User8', 'DEVOPSBand2', 'TaggedNAGAP'),
('User9', 'DEVOPSBand2', 'PotentailNAGP'),
('User10', 'DEVOPSBand2', 'TaggedNAGAP')
ON CONFLICT DO NOTHING;
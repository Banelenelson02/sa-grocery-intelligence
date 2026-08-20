INSERT INTO stores (name, chain, region) VALUES
    ('Pick n Pay', 'Pick n Pay', 'Gauteng'),
    ('Woolworths', 'Woolworths', 'Gauteng'),
    ('Checkers', 'Shoprite Holdings', 'Gauteng'),
    ('Shoprite', 'Shoprite Holdings', 'Western Cape')
ON CONFLICT (name) DO NOTHING;
-- =====================================================
-- SAUVEGARDE SCHEMA TEST - Script SQL
-- =====================================================
-- Usage: psql -h localhost -U postgres -d databook -f backup_schema_test.sql

-- Afficher les informations de début
\echo '🔒 SAUVEGARDE SCHEMA TEST'
\echo '========================'

-- 1. Vérifier les tables existantes dans le schéma test
\echo '📊 Tables existantes dans le schéma test:'
SELECT table_name, 
       (SELECT count(*) FROM information_schema.columns 
        WHERE table_schema = 'test' AND table_name = t.table_name) as nb_colonnes,
       pg_size_pretty(pg_total_relation_size('test.' || table_name)) as taille
FROM information_schema.tables t
WHERE table_schema = 'test'
ORDER BY table_name;

-- 2. Compter les lignes dans chaque table
\echo ''
\echo '📋 Nombre de lignes par table:'

DO $$
DECLARE
    table_record RECORD;
    row_count INTEGER;
    total_rows INTEGER := 0;
BEGIN
    -- Parcourir toutes les tables du schéma test
    FOR table_record IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'test' 
        ORDER BY table_name
    LOOP
        -- Compter les lignes
        EXECUTE format('SELECT count(*) FROM test.%I', table_record.table_name) INTO row_count;
        total_rows := total_rows + row_count;
        
        -- Afficher le résultat
        RAISE NOTICE '   • test.%: % lignes', table_record.table_name, row_count;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 Total: % lignes dans le schéma test', total_rows;
    
    IF total_rows = 0 THEN
        RAISE NOTICE '💡 Schéma test vide - pas de sauvegarde nécessaire';
    ELSE
        RAISE NOTICE '🎯 Démarrage de la sauvegarde...';
    END IF;
END $$;

-- 3. Créer le schéma de sauvegarde
\echo ''
\echo '📁 Création du schéma de sauvegarde...'
DROP SCHEMA IF EXISTS test_backup CASCADE;
CREATE SCHEMA test_backup;

-- 4. Sauvegarder toutes les tables
\echo '📦 Sauvegarde des tables...'

-- Tables principales
CREATE TABLE test_backup.livre AS SELECT * FROM test.livre;
\echo '✅ Table livre sauvegardée'

CREATE TABLE test_backup.auteur AS SELECT * FROM test.auteur;
\echo '✅ Table auteur sauvegardée'

CREATE TABLE test_backup.editeur AS SELECT * FROM test.editeur;
\echo '✅ Table editeur sauvegardée'

CREATE TABLE test_backup.langue AS SELECT * FROM test.langue;
\echo '✅ Table langue sauvegardée'

CREATE TABLE test_backup.sujet AS SELECT * FROM test.sujet;
\echo '✅ Table sujet sauvegardée'

-- Tables spéciales
CREATE TABLE test_backup.books AS SELECT * FROM test.books;
\echo '✅ Table books sauvegardée'

CREATE TABLE test_backup.users AS SELECT * FROM test.users;
\echo '✅ Table users sauvegardée'

CREATE TABLE test_backup.extraction_log AS SELECT * FROM test.extraction_log;
\echo '✅ Table extraction_log sauvegardée'

-- Tables de liaison
CREATE TABLE test_backup.livre_auteur AS SELECT * FROM test.livre_auteur;
\echo '✅ Table livre_auteur sauvegardée'

CREATE TABLE test_backup.livre_editeur AS SELECT * FROM test.livre_editeur;
\echo '✅ Table livre_editeur sauvegardée'

CREATE TABLE test_backup.livre_langue AS SELECT * FROM test.livre_langue;
\echo '✅ Table livre_langue sauvegardée'

CREATE TABLE test_backup.livre_sujet AS SELECT * FROM test.livre_sujet;
\echo '✅ Table livre_sujet sauvegardée'

-- 5. Vérifier la sauvegarde
\echo ''
\echo '🔍 Vérification de la sauvegarde:'

DO $$
DECLARE
    table_record RECORD;
    original_count INTEGER;
    backup_count INTEGER;
    total_backup_rows INTEGER := 0;
BEGIN
    FOR table_record IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'test_backup' 
        ORDER BY table_name
    LOOP
        -- Compter dans l'original et la sauvegarde
        EXECUTE format('SELECT count(*) FROM test.%I', table_record.table_name) INTO original_count;
        EXECUTE format('SELECT count(*) FROM test_backup.%I', table_record.table_name) INTO backup_count;
        total_backup_rows := total_backup_rows + backup_count;
        
        IF original_count = backup_count THEN
            RAISE NOTICE '✅ %: % lignes (OK)', table_record.table_name, backup_count;
        ELSE
            RAISE NOTICE '❌ %: % → % lignes (ERREUR)', table_record.table_name, original_count, backup_count;
        END IF;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 SAUVEGARDE TERMINÉE';
    RAISE NOTICE '📊 Total sauvegardé: % lignes dans test_backup', total_backup_rows;
    RAISE NOTICE '';
    RAISE NOTICE '💡 Pour restaurer:';
    RAISE NOTICE '   DROP SCHEMA test CASCADE;';
    RAISE NOTICE '   ALTER SCHEMA test_backup RENAME TO test;';
END $$;

-- 6. Afficher les schémas disponibles
\echo ''
\echo '📋 Schémas disponibles après sauvegarde:'
SELECT schema_name, 
       (SELECT count(*) FROM information_schema.tables WHERE table_schema = s.schema_name) as nb_tables
FROM information_schema.schemata s
WHERE schema_name IN ('test', 'test_backup', 'public')
ORDER BY schema_name; 
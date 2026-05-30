DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = 'econrg_store'
   ) THEN
      CREATE DATABASE econrg_store;
   END IF;
END
$$;
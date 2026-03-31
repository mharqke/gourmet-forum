import mysql.connector
from mysql.connector import Error
import sys

# Database configuration
db_config = {
    'host': 'quolimeplise.beget.app',
    'port': 3306,
    'database': 'gourments_db',
    'user': 'gourments_db',
    'password': 'F5DaC%wOznFW'
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(connection, query, params=None):
    """Execute a query (INSERT, UPDATE, DELETE)"""
    cursor = None
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
        return cursor.rowcount
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def fetch_data(connection, query, params=None):
    """Fetch data from database (SELECT queries)"""
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)  # Returns rows as dictionaries
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def main():
    # Create connection
    connection = create_connection()
    
    if not connection:
        print("Failed to connect to database. Exiting...")
        sys.exit(1)
    
    try:
        # Example 1: SELECT query - fetch all tables
        # print("\n--- Example 1: Show all tables ---")
        # tables = fetch_data(connection, "SHOW TABLES")
        # if tables:
        #     for table in tables:
        #         print(table)
        
        # Example 2: SELECT query with WHERE clause
        # print("\n--- Example 2: Fetch specific data ---")
        # Uncomment and modify based on your table structure
        # users = fetch_data(connection, "SELECT * FROM users WHERE id = %s", (1,))
        # if users:
        #     for user in users:
        #         print(user)
        
        # Example 3: INSERT query
        # print("\n--- Example 3: Insert data ---")
        # Uncomment and modify based on your table structure
        # insert_query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        # execute_query(connection, insert_query, ("John Doe", "john@example.com"))
        
        print('start')
        query = '''CREATE TABLE `comments` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `post_id` integer,
  `user_id` integer,
  `body` text,
  `created_at` timestamp,
  `comment_id` integer
);

CREATE TABLE `groups` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `user_id` integer,
  `title` varchar(255),
  `body` text,
  `created_at` timestamp
);

CREATE TABLE `users` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `username` varchar(255) UNIQUE,
  `email` varchar(255) UNIQUE,
  `password_hash` varchar(255),
  `created_at` timestamp,
  `city` varchar(255),
  `bio` text
);

CREATE TABLE `categories` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(255),
  `description` text,
  `created_at` timestamp
);

CREATE TABLE `posts` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `author_id` integer NOT NULL,
  `category_id` integer,
  `group_id` integer,
  `title` varchar(255),
  `content` text,
  `status` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `post_reactions` (
  `user_id` integer,
  `post_id` integer,
  `reaction` integer,
  `created_at` timestamp,
  PRIMARY KEY (`user_id`, `post_id`)
);

CREATE TABLE `tags` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(255) UNIQUE
);

CREATE TABLE `thread_tags` (
  `post_id` integer,
  `tag_id` integer,
  `created_at` timestamp,
  PRIMARY KEY (`post_id`, `tag_id`)
);

ALTER TABLE `comments` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`);

ALTER TABLE `post_reactions` ADD FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`);

ALTER TABLE `post_reactions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `posts` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);

ALTER TABLE `posts` ADD FOREIGN KEY (`author_id`) REFERENCES `users` (`id`);

ALTER TABLE `thread_tags` ADD FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`);

ALTER TABLE `thread_tags` ADD FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`);

ALTER TABLE `groups` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `posts` ADD FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`);

INSERT INTO categories (name, description) values ('Приготовление', 'Техники, советы и секреты готовки'),
('Ингредиенты', 'Всё о продуктах: выбор, свойства, применение'),
('Замена продуктов', 'Чем заменить ингредиент в рецепте'),
('Хранение', 'Как правильно хранить продукты и блюда'),
('Рестораны и кафе', 'Обзоры заведений, впечатления, рекомендации'),
('Продукты', 'Обсуждение качества, брендов и поставщиков'),
('Кухонная техника', 'Обзоры и советы по использованию устройств'),
('Гастро-события', 'Фестивали, мастер-классы и кулинарные встречи'),
('Домашняя еда', 'Простые и любимые блюда для семьи'),
('Холодные блюда', 'Салаты, закуски и освежающие рецепты'),
('Горячие блюда', 'Супы, вторые блюда и сытные угощения'),
('Десерты', 'Сладости, торты и кондитерские шедевры'),
('Выпечка', 'Хлеб, пироги, печенье и тесто');


--database gourments_db password Hbr!U*48UcDH'''
        for q in query.split(';'):
            print('working')
            execute_query(connection, q)
        print('end')

        # Example 4: UPDATE query
        # print("\n--- Example 4: Update data ---")
        # Uncomment and modify based on your table structure
        # update_query = "UPDATE users SET name = %s WHERE id = %s"
        # execute_query(connection, update_query, ("Jane Doe", 1))
        
        # Example 5: DELETE query
        # print("\n--- Example 5: Delete data ---")
        # Uncomment and modify based on your table structure
        # delete_query = "DELETE FROM users WHERE id = %s"
        # execute_query(connection, delete_query, (1,))
        
    finally:
        # Close connection
        if connection.is_connected():
            connection.close()
            print("\nMySQL connection closed")

if __name__ == "__main__":
    main()
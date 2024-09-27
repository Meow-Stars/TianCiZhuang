-- -- 这个文件存储建表相关的SQL语句，会在运行程序之初就执行
--
-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS post;
--
-- -- user表存储用户信息，主键、username、password
-- CREATE TABLE user (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username TEXT UNIQUE NOT NULL,
--     password TEXT NOT NULL
-- );
--
-- -- post存储所发的帖子，主键、作者id、创建时间、更新时间、标题、帖子内容、请求捐款的金额
-- CREATE TABLE post (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     author_id INTEGER NOT NULL,
--     created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     edited TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     title TEXT NOT NULL,
--     body TEXT NOT NULL,
--     money INTEGER NOT NULL,
--     FOREIGN KEY (author_id) REFERENCES user (id)
-- );

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS donate;

-- user表存储用户信息，主键、username、password
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTO_INCREMENT COMMENT '自增ID',
    username varchar(14) UNIQUE NOT NULL COMMENT '用户名',
    password TEXT NOT NULL COMMENT '密码'
) CHARACTER SET utf8 COLLATE utf8_general_ci;

-- post存储所发的帖子，主键、作者id、创建时间、更新时间、标题、帖子内容、请求捐款的金额
CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTO_INCREMENT COMMENT '自增ID',
    author_id INTEGER NOT NULL COMMENT '作者ID',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    edited TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    title TEXT NOT NULL COMMENT '帖子标题',
    body TEXT NOT NULL COMMENT '帖子正文',
    money INTEGER NOT NULL COMMENT '求助金额',
    FOREIGN KEY (author_id) REFERENCES user (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

-- donate存储捐款金额，主键、帖子id、捐款人id、捐款金额、捐款时间
CREATE TABLE donate (
    id INTEGER PRIMARY KEY AUTO_INCREMENT COMMENT '自增ID',
    post_id INTEGER NOT NULL COMMENT '帖子ID',
    donor_id INTEGER NOT NULL COMMENT '作者ID',
    amount INTEGER NOT NULL COMMENT '捐款金额',
    happened TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '捐款时间',
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (donor_id) REFERENCES user (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

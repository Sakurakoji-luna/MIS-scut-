-- ==========================================================
-- MIS 系统初始数据库脚本
-- 适用数据库：MySQL / MariaDB
-- 字符集：utf8mb4 (支持多语言及特殊符号) 
-- ==========================================================

-- 1. 创建数据库 (如果不存在) 
CREATE DATABASE IF NOT EXISTS `scut_mis` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `scut_mis`;

-- 2. 暂时关闭外键检查，以便干净地重建表结构 
SET FOREIGN_KEY_CHECKS = 0;

-- 3. 清理旧表 (防止结构冲突) 
DROP TABLE IF EXISTS `CourseChoosing`;
DROP TABLE IF EXISTS `Courses`;
DROP TABLE IF EXISTS `Teachers`;
DROP TABLE IF EXISTS `Students`;
DROP TABLE IF EXISTS `AccountPassword`;

-- 4. 创建 Students (学生) 表 
CREATE TABLE `Students` (
    `StudentID` VARCHAR(10) PRIMARY KEY,
    `StudentName` VARCHAR(50) NOT NULL,
    `Sex` VARCHAR(10),
    `EntranceAge` INTEGER,
    `EntranceYear` INTEGER NOT NULL,
    `Class` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 创建 Teachers (教师) 表 
CREATE TABLE `Teachers` (
    `TeacherID` VARCHAR(5) PRIMARY KEY,
    `TeacherName` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 创建 Courses (课程) 表 
CREATE TABLE `Courses` (
    `CourseID` VARCHAR(7) PRIMARY KEY,
    `CourseName` VARCHAR(100) NOT NULL,
    `TeacherID` VARCHAR(5) NOT NULL,
    `Credit` FLOAT NOT NULL,
    `Grade INTEGER` NOT NULL,
    `CanceledYear` INTEGER,
    CONSTRAINT `fk_courses_teacher` FOREIGN KEY (`TeacherID`) REFERENCES `Teachers` (`TeacherID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 创建 CourseChoosing (选课) 表 
CREATE TABLE `CourseChoosing` (
    `StudentID` VARCHAR(10) NOT NULL,
    `CourseID` VARCHAR(7) NOT NULL,
    `TeacherID` VARCHAR(5) NOT NULL,
    `ChosenYear` INTEGER NOT NULL,
    `Score` FLOAT,
    PRIMARY KEY (`StudentID`, `CourseID`, `TeacherID`),
    CONSTRAINT `fk_cc_student` FOREIGN KEY (`StudentID`) REFERENCES `Students` (`StudentID`) ON DELETE CASCADE,
    CONSTRAINT `fk_cc_course` FOREIGN KEY (`CourseID`) REFERENCES `Courses` (`CourseID`),
    CONSTRAINT `fk_cc_teacher` FOREIGN KEY (`TeacherID`) REFERENCES `Teachers` (`TeacherID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 创建 AccountPassword (账号密码) 表 
CREATE TABLE `AccountPassword` (
    `Account` VARCHAR(20) PRIMARY KEY,
    `Occupation` VARCHAR(20),
    `Password` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 注入初始演示数据 
-- 插入账号 (初始密码均为 123456) 
INSERT INTO `AccountPassword` VALUES 
('2020000001', 'student', '123456'),
('2021000001', 'student', '123456'),
('2022000001', 'student', '123456'),
('00001', 'teacher', '123456'),
('00002', 'teacher', '123456'),
('00000', 'admin', '123456');

-- 插入教师信息 
INSERT INTO `Teachers` VALUES 
('00001', 'Smith'), 
('00002', 'Johnson'), 
('00003', 'Williams');

-- 插入学生信息 
INSERT INTO `Students` VALUES 
('2022000001', 'Alice', 'female', 18, 2022, 'Class 1'),
('2020000001', 'Charlie', 'male', 22, 2020, 'Class 3');

-- 10. 恢复外键检查并提交 
SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
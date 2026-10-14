-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: hrms_db
-- ------------------------------------------------------
-- Server version	8.0.38

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `must_change_password` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `accounts_user_role_57e97df0` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'pbkdf2_sha256$1000000$YtOJIo1DJbRaCY2t4kCZpy$T/slPBPj5b6zHrmO+PpncSaAH+hvfUHNifvIzDca6po=',NULL,1,'admin','Admin','User',1,1,'2026-10-12 15:19:49.039412','admin@hrms.local','ADMIN',0),(2,'pbkdf2_sha256$1000000$rKa3NjkbchXhgnBztjRvKn$ISkSnyv03gvabEQ+dXtcFzZn7i7FjKQYhhY3YEi0810=',NULL,0,'hr','Helen','Roberts',0,1,'2026-10-12 15:19:49.482585','hr@hrms.local','HR',0),(3,'pbkdf2_sha256$1000000$EisXqXipnWVkd9HmtUpLIB$o7eEZU2Imv44ULl6MhPmy3Hmz4dloE8qCdLI0ED9fw0=',NULL,0,'dinesh','Dinesh','Kumar',0,1,'2026-10-12 15:19:49.900943','dinesh@hrms.local','EMPLOYEE',0),(4,'pbkdf2_sha256$1000000$9SXBxU28B1xsgIBd0LmDJj$WOxro9zSPZg7Q04Had95rrzeY9OrHQZB5V14APGA0Wc=',NULL,0,'priya','Priya','Sharma',0,1,'2026-10-12 15:19:50.320519','priya@hrms.local','EMPLOYEE',0),(5,'pbkdf2_sha256$1000000$vLH9JZQbX2Wq5SVaXjtuJM$+wAYsrJy+0BUSLt84wMN7+27hE7SDezynF2J6XEfyvk=',NULL,0,'arun','Arun','Raj',0,1,'2026-10-12 15:19:50.743451','arun@hrms.local','EMPLOYEE',0),(6,'pbkdf2_sha256$1000000$v8ljkOOsh6VvNPPRdpRa40$j0RyEbUQE6uB/v1L3SBmQIECGARCBUUu21N58iXbVo0=',NULL,0,'meena','Meena','Iyer',0,1,'2026-10-12 15:19:51.170903','meena@hrms.local','EMPLOYEE',0),(7,'pbkdf2_sha256$1000000$6gnVyU0rSsQ4gbqpkufgaO$ohSHAt5yNtjFJGkTK7Rixnrc3MyArK3wabL/I/+BPjc=','2026-10-13 04:15:02.666280',1,'Dk','','',1,1,'2026-10-12 15:25:35.518399','dineshkumarsenthilk123@gmail.com','ADMIN',0);
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_attendance`
--

DROP TABLE IF EXISTS `attendance_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_attendance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `check_in` datetime(6) DEFAULT NULL,
  `check_out` datetime(6) DEFAULT NULL,
  `working_hours` decimal(5,2) NOT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_overridden` tinyint(1) NOT NULL,
  `override_note` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_id` bigint NOT NULL,
  `overridden_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `one_attendance_per_day` (`employee_id`,`date`),
  KEY `attendance_attendanc_overridden_by_id_0783d430_fk_accounts_` (`overridden_by_id`),
  KEY `attendance_attendance_date_3c949aa8` (`date`),
  KEY `attendance__employe_08d913_idx` (`employee_id`,`date`),
  CONSTRAINT `attendance_attendanc_employee_id_63b4db5a_fk_employees` FOREIGN KEY (`employee_id`) REFERENCES `employees_employee` (`id`),
  CONSTRAINT `attendance_attendanc_overridden_by_id_0783d430_fk_accounts_` FOREIGN KEY (`overridden_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_attendance`
--

LOCK TABLES `attendance_attendance` WRITE;
/*!40000 ALTER TABLE `attendance_attendance` DISABLE KEYS */;
INSERT INTO `attendance_attendance` VALUES (1,'2026-09-01','2026-09-01 03:39:00.000000','2026-09-01 12:04:00.000000',8.42,'PRESENT',0,'',1,NULL),(2,'2026-09-02','2026-09-02 03:34:00.000000','2026-09-02 12:08:00.000000',8.57,'PRESENT',0,'',1,NULL),(3,'2026-09-03','2026-09-03 04:07:00.000000','2026-09-03 12:10:00.000000',8.05,'PRESENT',0,'',1,NULL),(4,'2026-09-04','2026-09-04 03:43:00.000000','2026-09-04 11:45:00.000000',8.03,'PRESENT',0,'',1,NULL),(5,'2026-09-07','2026-09-07 03:56:00.000000','2026-09-07 12:00:00.000000',8.07,'PRESENT',0,'',1,NULL),(6,'2026-09-08','2026-09-08 04:05:00.000000','2026-09-08 12:32:00.000000',8.45,'PRESENT',0,'',1,NULL),(7,'2026-09-10','2026-09-10 03:44:00.000000','2026-09-10 12:24:00.000000',8.67,'PRESENT',0,'',1,NULL),(8,'2026-09-11','2026-09-11 03:33:00.000000','2026-09-11 12:09:00.000000',8.60,'PRESENT',0,'',1,NULL),(9,'2026-09-14','2026-09-14 03:33:00.000000','2026-09-14 11:47:00.000000',8.23,'PRESENT',0,'',1,NULL),(10,'2026-09-16','2026-09-16 03:48:00.000000','2026-09-16 12:14:00.000000',8.43,'PRESENT',0,'',1,NULL),(11,'2026-09-17','2026-09-17 03:37:00.000000','2026-09-17 12:13:00.000000',8.60,'PRESENT',0,'',1,NULL),(12,'2026-09-18','2026-09-18 03:41:00.000000','2026-09-18 11:47:00.000000',8.10,'PRESENT',0,'',1,NULL),(13,'2026-09-21','2026-09-21 04:10:00.000000','2026-09-21 12:22:00.000000',8.20,'PRESENT',0,'',1,NULL),(14,'2026-09-22','2026-09-22 04:05:00.000000','2026-09-22 12:50:00.000000',8.75,'PRESENT',0,'',1,NULL),(15,'2026-09-23','2026-09-23 03:33:00.000000','2026-09-23 12:12:00.000000',8.65,'PRESENT',0,'',1,NULL),(16,'2026-09-24','2026-09-24 04:04:00.000000','2026-09-24 12:31:00.000000',8.45,'PRESENT',0,'',1,NULL),(17,'2026-09-25','2026-09-25 03:59:00.000000','2026-09-25 12:36:00.000000',8.62,'PRESENT',0,'',1,NULL),(18,'2026-09-28','2026-09-28 03:53:00.000000','2026-09-28 12:12:00.000000',8.32,'PRESENT',0,'',1,NULL),(19,'2026-09-29','2026-09-29 03:41:00.000000','2026-09-29 12:25:00.000000',8.73,'PRESENT',0,'',1,NULL),(20,'2026-09-30','2026-09-30 03:35:00.000000','2026-09-30 12:11:00.000000',8.60,'PRESENT',0,'',1,NULL),(21,'2026-09-01','2026-09-01 04:01:00.000000','2026-09-01 12:22:00.000000',8.35,'PRESENT',0,'',2,NULL),(22,'2026-09-02','2026-09-02 03:48:00.000000','2026-09-02 12:26:00.000000',8.63,'PRESENT',0,'',2,NULL),(23,'2026-09-03','2026-09-03 03:37:00.000000','2026-09-03 12:09:00.000000',8.53,'PRESENT',0,'',2,NULL),(24,'2026-09-04','2026-09-04 03:51:00.000000','2026-09-04 12:00:00.000000',8.15,'PRESENT',0,'',2,NULL),(25,'2026-09-07','2026-09-07 03:56:00.000000','2026-09-07 11:58:00.000000',8.03,'PRESENT',0,'',2,NULL),(26,'2026-09-08','2026-09-08 03:34:00.000000','2026-09-08 12:09:00.000000',8.58,'PRESENT',0,'',2,NULL),(27,'2026-09-09','2026-09-09 03:50:00.000000','2026-09-09 12:11:00.000000',8.35,'PRESENT',0,'',2,NULL),(28,'2026-09-10','2026-09-10 04:08:00.000000','2026-09-10 12:39:00.000000',8.52,'PRESENT',0,'',2,NULL),(29,'2026-09-11','2026-09-11 03:59:00.000000','2026-09-11 12:03:00.000000',8.07,'PRESENT',0,'',2,NULL),(30,'2026-09-14','2026-09-14 03:47:00.000000','2026-09-14 12:17:00.000000',8.50,'PRESENT',0,'',2,NULL),(31,'2026-09-15','2026-09-15 03:34:00.000000','2026-09-15 11:37:00.000000',8.05,'PRESENT',0,'',2,NULL),(32,'2026-09-16','2026-09-16 03:49:00.000000','2026-09-16 12:30:00.000000',8.68,'PRESENT',0,'',2,NULL),(33,'2026-09-17','2026-09-17 03:58:00.000000','2026-09-17 12:16:00.000000',8.30,'PRESENT',0,'',2,NULL),(34,'2026-09-18','2026-09-18 03:52:00.000000','2026-09-18 11:53:00.000000',8.02,'PRESENT',0,'',2,NULL),(35,'2026-09-21','2026-09-21 03:52:00.000000','2026-09-21 12:02:00.000000',8.17,'PRESENT',0,'',2,NULL),(36,'2026-09-22','2026-09-22 04:01:00.000000','2026-09-22 12:04:00.000000',8.05,'PRESENT',0,'',2,NULL),(37,'2026-09-23','2026-09-23 03:48:00.000000','2026-09-23 11:56:00.000000',8.13,'PRESENT',0,'',2,NULL),(38,'2026-09-24','2026-09-24 03:55:00.000000','2026-09-24 12:20:00.000000',8.42,'PRESENT',0,'',2,NULL),(39,'2026-09-25','2026-09-25 04:01:00.000000','2026-09-25 12:06:00.000000',8.08,'PRESENT',0,'',2,NULL),(40,'2026-09-28','2026-09-28 03:55:00.000000','2026-09-28 12:30:00.000000',8.58,'PRESENT',0,'',2,NULL),(41,'2026-09-29','2026-09-29 03:38:00.000000','2026-09-29 12:05:00.000000',8.45,'PRESENT',0,'',2,NULL),(42,'2026-09-30','2026-09-30 03:47:00.000000','2026-09-30 12:32:00.000000',8.75,'PRESENT',0,'',2,NULL),(43,'2026-09-01','2026-09-01 03:52:00.000000','2026-09-01 12:35:00.000000',8.72,'PRESENT',0,'',3,NULL),(44,'2026-09-02','2026-09-02 03:44:00.000000','2026-09-02 11:53:00.000000',8.15,'PRESENT',0,'',3,NULL),(45,'2026-09-03','2026-09-03 03:39:00.000000','2026-09-03 11:53:00.000000',8.23,'PRESENT',0,'',3,NULL),(46,'2026-09-04','2026-09-04 03:30:00.000000','2026-09-04 12:01:00.000000',8.52,'PRESENT',0,'',3,NULL),(47,'2026-09-07','2026-09-07 03:41:00.000000','2026-09-07 11:57:00.000000',8.27,'PRESENT',0,'',3,NULL),(48,'2026-09-08','2026-09-08 03:39:00.000000','2026-09-08 12:05:00.000000',8.43,'PRESENT',0,'',3,NULL),(49,'2026-09-09','2026-09-09 04:09:00.000000','2026-09-09 12:45:00.000000',8.60,'PRESENT',0,'',3,NULL),(50,'2026-09-10','2026-09-10 03:38:00.000000','2026-09-10 12:22:00.000000',8.73,'PRESENT',0,'',3,NULL),(51,'2026-09-11','2026-09-11 04:09:00.000000','2026-09-11 12:50:00.000000',8.68,'PRESENT',0,'',3,NULL),(52,'2026-09-14','2026-09-14 03:33:00.000000','2026-09-14 12:02:00.000000',8.48,'PRESENT',0,'',3,NULL),(53,'2026-09-15','2026-09-15 04:05:00.000000','2026-09-15 12:30:00.000000',8.42,'PRESENT',0,'',3,NULL),(54,'2026-09-16','2026-09-16 03:55:00.000000','2026-09-16 12:01:00.000000',8.10,'PRESENT',0,'',3,NULL),(55,'2026-09-17','2026-09-17 03:55:00.000000','2026-09-17 11:58:00.000000',8.05,'PRESENT',0,'',3,NULL),(56,'2026-09-18','2026-09-18 03:43:00.000000','2026-09-18 12:11:00.000000',8.47,'PRESENT',0,'',3,NULL),(57,'2026-09-21','2026-09-21 03:51:00.000000','2026-09-21 12:29:00.000000',8.63,'PRESENT',0,'',3,NULL),(58,'2026-09-24','2026-09-24 03:36:00.000000','2026-09-24 11:59:00.000000',8.38,'PRESENT',0,'',3,NULL),(59,'2026-09-25','2026-09-25 03:34:00.000000','2026-09-25 11:47:00.000000',8.22,'PRESENT',0,'',3,NULL),(60,'2026-09-28','2026-09-28 03:39:00.000000','2026-09-28 12:19:00.000000',8.67,'PRESENT',0,'',3,NULL),(61,'2026-09-29','2026-09-29 03:52:00.000000','2026-09-29 12:30:00.000000',8.63,'PRESENT',0,'',3,NULL),(62,'2026-09-30','2026-09-30 03:37:00.000000','2026-09-30 11:44:00.000000',8.12,'PRESENT',0,'',3,NULL),(63,'2026-09-01','2026-09-01 03:59:00.000000','2026-09-01 12:29:00.000000',8.50,'PRESENT',0,'',4,NULL),(64,'2026-09-02','2026-09-02 03:35:00.000000','2026-09-02 11:44:00.000000',8.15,'PRESENT',0,'',4,NULL),(65,'2026-09-03','2026-09-03 03:51:00.000000','2026-09-03 12:07:00.000000',8.27,'PRESENT',0,'',4,NULL),(66,'2026-09-04','2026-09-04 03:40:00.000000','2026-09-04 12:13:00.000000',8.55,'PRESENT',0,'',4,NULL),(67,'2026-09-08','2026-09-08 04:03:00.000000','2026-09-08 12:26:00.000000',8.38,'PRESENT',0,'',4,NULL),(68,'2026-09-09','2026-09-09 04:04:00.000000','2026-09-09 12:05:00.000000',8.02,'PRESENT',0,'',4,NULL),(69,'2026-09-10','2026-09-10 03:49:00.000000','2026-09-10 12:30:00.000000',8.68,'PRESENT',0,'',4,NULL),(70,'2026-09-11','2026-09-11 03:46:00.000000','2026-09-11 12:19:00.000000',8.55,'PRESENT',0,'',4,NULL),(71,'2026-09-14','2026-09-14 03:40:00.000000','2026-09-14 12:02:00.000000',8.37,'PRESENT',0,'',4,NULL),(72,'2026-09-15','2026-09-15 04:04:00.000000','2026-09-15 12:38:00.000000',8.57,'PRESENT',0,'',4,NULL),(73,'2026-09-16','2026-09-16 03:51:00.000000','2026-09-16 12:31:00.000000',8.67,'PRESENT',0,'',4,NULL),(74,'2026-09-17','2026-09-17 03:42:00.000000','2026-09-17 11:57:00.000000',8.25,'PRESENT',0,'',4,NULL),(75,'2026-09-18','2026-09-18 03:44:00.000000','2026-09-18 11:56:00.000000',8.20,'PRESENT',0,'',4,NULL),(76,'2026-09-21','2026-09-21 03:52:00.000000','2026-09-21 11:53:00.000000',8.02,'PRESENT',0,'',4,NULL),(77,'2026-09-22','2026-09-22 03:47:00.000000','2026-09-22 12:17:00.000000',8.50,'PRESENT',0,'',4,NULL),(78,'2026-09-23','2026-09-23 04:08:00.000000','2026-09-23 12:30:00.000000',8.37,'PRESENT',0,'',4,NULL),(79,'2026-09-24','2026-09-24 03:52:00.000000','2026-09-24 12:15:00.000000',8.38,'PRESENT',0,'',4,NULL),(80,'2026-09-25','2026-09-25 03:36:00.000000','2026-09-25 11:50:00.000000',8.23,'PRESENT',0,'',4,NULL),(81,'2026-09-28','2026-09-28 03:51:00.000000','2026-09-28 12:04:00.000000',8.22,'PRESENT',0,'',4,NULL),(82,'2026-09-29','2026-09-29 04:09:00.000000','2026-09-29 12:09:00.000000',8.00,'PRESENT',0,'',4,NULL),(83,'2026-09-30','2026-09-30 03:52:00.000000','2026-09-30 12:33:00.000000',8.68,'PRESENT',0,'',4,NULL),(84,'2026-09-01','2026-09-01 03:37:00.000000','2026-09-01 12:01:00.000000',8.40,'PRESENT',0,'',5,NULL),(85,'2026-09-02','2026-09-02 03:42:00.000000','2026-09-02 12:12:00.000000',8.50,'PRESENT',0,'',5,NULL),(86,'2026-09-03','2026-09-03 03:57:00.000000','2026-09-03 12:37:00.000000',8.67,'PRESENT',0,'',5,NULL),(87,'2026-09-04','2026-09-04 03:55:00.000000','2026-09-04 12:24:00.000000',8.48,'PRESENT',0,'',5,NULL),(88,'2026-09-07','2026-09-07 03:35:00.000000','2026-09-07 11:45:00.000000',8.17,'PRESENT',0,'',5,NULL),(89,'2026-09-08','2026-09-08 03:38:00.000000','2026-09-08 11:39:00.000000',8.02,'PRESENT',0,'',5,NULL),(90,'2026-09-09','2026-09-09 03:59:00.000000','2026-09-09 12:40:00.000000',8.68,'PRESENT',0,'',5,NULL),(91,'2026-09-10','2026-09-10 04:08:00.000000','2026-09-10 12:38:00.000000',8.50,'PRESENT',0,'',5,NULL),(92,'2026-09-11','2026-09-11 03:52:00.000000','2026-09-11 12:01:00.000000',8.15,'PRESENT',0,'',5,NULL),(93,'2026-09-14','2026-09-14 03:38:00.000000','2026-09-14 11:39:00.000000',8.02,'PRESENT',0,'',5,NULL),(94,'2026-09-16','2026-09-16 03:36:00.000000','2026-09-16 12:09:00.000000',8.55,'PRESENT',0,'',5,NULL),(95,'2026-09-17','2026-09-17 03:38:00.000000','2026-09-17 12:05:00.000000',8.45,'PRESENT',0,'',5,NULL),(96,'2026-09-18','2026-09-18 03:42:00.000000','2026-09-18 11:55:00.000000',8.22,'PRESENT',0,'',5,NULL),(97,'2026-09-22','2026-09-22 04:02:00.000000','2026-09-22 12:17:00.000000',8.25,'PRESENT',0,'',5,NULL),(98,'2026-09-23','2026-09-23 03:50:00.000000','2026-09-23 12:06:00.000000',8.27,'PRESENT',0,'',5,NULL),(99,'2026-09-24','2026-09-24 03:38:00.000000','2026-09-24 11:41:00.000000',8.05,'PRESENT',0,'',5,NULL),(100,'2026-09-25','2026-09-25 03:52:00.000000','2026-09-25 12:21:00.000000',8.48,'PRESENT',0,'',5,NULL),(101,'2026-09-28','2026-09-28 04:03:00.000000','2026-09-28 12:29:00.000000',8.43,'PRESENT',0,'',5,NULL),(102,'2026-09-29','2026-09-29 04:02:00.000000','2026-09-29 12:10:00.000000',8.13,'PRESENT',0,'',5,NULL),(103,'2026-09-30','2026-09-30 04:03:00.000000','2026-09-30 12:35:00.000000',8.53,'PRESENT',0,'',5,NULL),(104,'2026-09-02','2026-09-02 03:41:00.000000','2026-09-02 12:19:00.000000',8.63,'PRESENT',0,'',6,NULL),(105,'2026-09-04','2026-09-04 03:41:00.000000','2026-09-04 11:50:00.000000',8.15,'PRESENT',0,'',6,NULL),(106,'2026-09-07','2026-09-07 03:37:00.000000','2026-09-07 12:12:00.000000',8.58,'PRESENT',0,'',6,NULL),(107,'2026-09-08','2026-09-08 04:03:00.000000','2026-09-08 12:36:00.000000',8.55,'PRESENT',0,'',6,NULL),(108,'2026-09-09','2026-09-09 03:36:00.000000','2026-09-09 12:11:00.000000',8.58,'PRESENT',0,'',6,NULL),(109,'2026-09-11','2026-09-11 03:32:00.000000','2026-09-11 11:38:00.000000',8.10,'PRESENT',0,'',6,NULL),(110,'2026-09-14','2026-09-14 04:05:00.000000','2026-09-14 12:06:00.000000',8.02,'PRESENT',0,'',6,NULL),(111,'2026-09-15','2026-09-15 03:34:00.000000','2026-09-15 12:02:00.000000',8.47,'PRESENT',0,'',6,NULL),(112,'2026-09-16','2026-09-16 04:02:00.000000','2026-09-16 12:40:00.000000',8.63,'PRESENT',0,'',6,NULL),(113,'2026-09-17','2026-09-17 03:47:00.000000','2026-09-17 12:15:00.000000',8.47,'PRESENT',0,'',6,NULL),(114,'2026-09-18','2026-09-18 04:00:00.000000','2026-09-18 12:32:00.000000',8.53,'PRESENT',0,'',6,NULL),(115,'2026-09-21','2026-09-21 04:03:00.000000','2026-09-21 12:19:00.000000',8.27,'PRESENT',0,'',6,NULL),(116,'2026-09-22','2026-09-22 03:42:00.000000','2026-09-22 12:10:00.000000',8.47,'PRESENT',0,'',6,NULL),(117,'2026-09-23','2026-09-23 03:37:00.000000','2026-09-23 12:02:00.000000',8.42,'PRESENT',0,'',6,NULL),(118,'2026-09-24','2026-09-24 03:34:00.000000','2026-09-24 12:16:00.000000',8.70,'PRESENT',0,'',6,NULL),(119,'2026-09-25','2026-09-25 03:34:00.000000','2026-09-25 11:47:00.000000',8.22,'PRESENT',0,'',6,NULL),(120,'2026-09-28','2026-09-28 03:37:00.000000','2026-09-28 11:46:00.000000',8.15,'PRESENT',0,'',6,NULL),(121,'2026-09-29','2026-09-29 03:53:00.000000','2026-09-29 12:02:00.000000',8.15,'PRESENT',0,'',6,NULL),(122,'2026-09-30','2026-09-30 03:38:00.000000','2026-09-30 12:07:00.000000',8.48,'PRESENT',0,'',6,NULL),(123,'2026-10-13','2026-10-13 04:13:37.544101','2026-10-13 11:44:18.504446',7.51,'PRESENT',0,'',1,NULL),(124,'2026-10-14','2026-10-14 04:28:44.920651',NULL,0.00,'PRESENT',0,'',1,NULL),(125,'2026-10-14','2026-10-14 04:37:21.493338',NULL,0.00,'PRESENT',0,'',3,NULL);
/*!40000 ALTER TABLE `attendance_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_auditlog`
--

DROP TABLE IF EXISTS `audit_auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_auditlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_id` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `details` json NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_auditlog_user_id_c1cca96c_fk_accounts_user_id` (`user_id`),
  KEY `audit_auditlog_action_dc562e21` (`action`),
  KEY `audit_auditlog_entity_06a2a124` (`entity`),
  KEY `audit_auditlog_created_at_5c532845` (`created_at`),
  CONSTRAINT `audit_auditlog_user_id_c1cca96c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_auditlog`
--

LOCK TABLES `audit_auditlog` WRITE;
/*!40000 ALTER TABLE `audit_auditlog` DISABLE KEYS */;
INSERT INTO `audit_auditlog` VALUES (1,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-12 15:29:48.813236',7),(2,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-12 15:30:13.258119',7),(3,'admin','LOGIN','User','1','{}','127.0.0.1','2026-10-12 15:32:04.435740',1),(4,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-13 04:12:57.430370',7),(5,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-13 04:13:13.038226',7),(6,'admin','LOGIN','User','1','{}','127.0.0.1','2026-10-13 04:13:25.262456',1),(7,'admin','CHECK_IN','Attendance','123','{}','127.0.0.1','2026-10-13 04:13:37.553330',1),(8,'admin','USER_UPDATE','User','7','{\"new\": {\"role\": \"ADMIN\", \"is_active\": true}, \"old\": {\"role\": \"EMPLOYEE\", \"is_active\": true}}','127.0.0.1','2026-10-13 04:14:09.562785',1),(9,'admin','PAYROLL_GENERATE','Payroll','1','{\"net\": \"119109.09\", \"period\": \"2026-09\", \"employee\": \"EMP001\"}','127.0.0.1','2026-10-13 04:51:01.336797',1),(10,'admin','PAYROLL_GENERATE','Payroll','2','{\"net\": \"102600.00\", \"period\": \"2026-09\", \"employee\": \"EMP002\"}','127.0.0.1','2026-10-13 04:51:01.569585',1),(11,'admin','PAYROLL_GENERATE','Payroll','3','{\"net\": \"65727.27\", \"period\": \"2026-09\", \"employee\": \"EMP003\"}','127.0.0.1','2026-10-13 04:51:01.655921',1),(12,'admin','PAYROLL_GENERATE','Payroll','4','{\"net\": \"62327.27\", \"period\": \"2026-09\", \"employee\": \"EMP004\"}','127.0.0.1','2026-10-13 04:51:01.738515',1),(13,'admin','PAYROLL_GENERATE','Payroll','5','{\"net\": \"55050.91\", \"period\": \"2026-09\", \"employee\": \"EMP005\"}','127.0.0.1','2026-10-13 04:51:01.825117',1),(14,'admin','PAYROLL_GENERATE','Payroll','6','{\"net\": \"49472.73\", \"period\": \"2026-09\", \"employee\": \"EMP006\"}','127.0.0.1','2026-10-13 04:51:01.918676',1),(15,'admin','CHECK_OUT','Attendance','123','{\"hours\": \"7.51\"}','127.0.0.1','2026-10-13 11:44:18.514800',1),(16,'admin','SLIP_DOWNLOAD','Payroll','1','{}','127.0.0.1','2026-10-13 11:45:12.447169',1),(17,'admin','LOGOUT','User','1','{}','127.0.0.1','2026-10-13 12:12:35.994262',1),(18,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-13 12:12:46.931876',7),(19,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-13 12:14:45.031036',7),(20,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-13 12:15:04.360818',7),(21,'admin','LOGOUT','User','1','{}','127.0.0.1','2026-10-13 12:17:00.743696',1),(22,'admin','LOGIN','User','1','{}','127.0.0.1','2026-10-13 13:33:54.834031',1),(23,'admin','LOGIN','User','1','{}','127.0.0.1','2026-10-14 04:28:42.952230',1),(24,'admin','CHECK_IN','Attendance','124','{}','127.0.0.1','2026-10-14 04:28:44.924494',1),(25,'admin','LOGOUT','User','1','{}','127.0.0.1','2026-10-14 04:28:50.516697',1),(26,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:28:57.440371',7),(27,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:29:41.698231',7),(28,'admin','LOGIN','User','1','{}','127.0.0.1','2026-10-14 04:30:05.288667',1),(29,'admin','USER_UPDATE','User','7','{\"new\": {\"role\": \"EMPLOYEE\", \"is_active\": true}, \"old\": {\"role\": \"ADMIN\", \"is_active\": true}}','127.0.0.1','2026-10-14 04:30:15.897154',1),(30,'admin','LOGOUT','User','1','{}','127.0.0.1','2026-10-14 04:30:54.647632',1),(31,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:31:00.869385',7),(32,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:32:27.702302',7),(33,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:34:00.168344',7),(34,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:34:39.716400',7),(35,'dinesh','LOGIN','User','3','{}','127.0.0.1','2026-10-14 04:37:16.831030',3),(36,'dinesh','CHECK_IN','Attendance','125','{}','127.0.0.1','2026-10-14 04:37:21.498977',3),(37,'dinesh','LOGOUT','User','3','{}','127.0.0.1','2026-10-14 04:47:47.902364',3),(38,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:48:02.517114',7),(39,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:49:16.772775',7),(40,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:49:47.830238',7),(41,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:52:18.413636',7),(42,'hr','LOGIN','User','2','{}','127.0.0.1','2026-10-14 04:52:32.748999',2),(43,'hr','LOGOUT','User','2','{}','127.0.0.1','2026-10-14 04:53:38.025746',2),(44,'dinesh','LOGIN','User','3','{}','127.0.0.1','2026-10-14 04:54:06.547301',3),(45,'dinesh','SLIP_DOWNLOAD','Payroll','3','{}','127.0.0.1','2026-10-14 04:55:32.799919',3),(46,'dinesh','LOGOUT','User','3','{}','127.0.0.1','2026-10-14 04:56:21.693545',3),(47,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 04:56:28.245239',7),(48,'Dk','LOGOUT','User','7','{}','127.0.0.1','2026-10-14 04:57:07.288752',7),(49,'dinesh','LOGIN','User','3','{}','127.0.0.1','2026-10-14 04:57:32.119694',3),(50,'dinesh','LEAVE_APPLY','LeaveRequest','1','{\"days\": \"1\", \"lop_days\": \"0\"}','127.0.0.1','2026-10-14 04:58:01.911019',3),(51,'dinesh','LOGOUT','User','3','{}','127.0.0.1','2026-10-14 04:58:20.540786',3),(52,'hr','LOGIN','User','2','{}','127.0.0.1','2026-10-14 04:58:44.901817',2),(53,'hr','LEAVE_APPROVE','LeaveRequest','1','{\"employee\": \"EMP003\", \"lop_days\": \"0\"}','127.0.0.1','2026-10-14 04:59:16.357059',2),(54,'hr','LOGOUT','User','2','{}','127.0.0.1','2026-10-14 04:59:34.210175',2),(55,'dinesh','LOGIN','User','3','{}','127.0.0.1','2026-10-14 05:00:13.055294',3),(56,'dinesh','LOGOUT','User','3','{}','127.0.0.1','2026-10-14 05:16:50.839516',3),(57,'Dk','LOGIN','User','7','{}','127.0.0.1','2026-10-14 05:16:58.373367',7);
/*!40000 ALTER TABLE `audit_auditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Blacklisted Token',6,'add_blacklistedtoken'),(22,'Can change Blacklisted Token',6,'change_blacklistedtoken'),(23,'Can delete Blacklisted Token',6,'delete_blacklistedtoken'),(24,'Can view Blacklisted Token',6,'view_blacklistedtoken'),(25,'Can add Outstanding Token',7,'add_outstandingtoken'),(26,'Can change Outstanding Token',7,'change_outstandingtoken'),(27,'Can delete Outstanding Token',7,'delete_outstandingtoken'),(28,'Can view Outstanding Token',7,'view_outstandingtoken'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add department',9,'add_department'),(34,'Can change department',9,'change_department'),(35,'Can delete department',9,'delete_department'),(36,'Can view department',9,'view_department'),(37,'Can add employee',10,'add_employee'),(38,'Can change employee',10,'change_employee'),(39,'Can delete employee',10,'delete_employee'),(40,'Can view employee',10,'view_employee'),(41,'Can add employee document',11,'add_employeedocument'),(42,'Can change employee document',11,'change_employeedocument'),(43,'Can delete employee document',11,'delete_employeedocument'),(44,'Can view employee document',11,'view_employeedocument'),(45,'Can add attendance',12,'add_attendance'),(46,'Can change attendance',12,'change_attendance'),(47,'Can delete attendance',12,'delete_attendance'),(48,'Can view attendance',12,'view_attendance'),(49,'Can add leave type',13,'add_leavetype'),(50,'Can change leave type',13,'change_leavetype'),(51,'Can delete leave type',13,'delete_leavetype'),(52,'Can view leave type',13,'view_leavetype'),(53,'Can add leave request',14,'add_leaverequest'),(54,'Can change leave request',14,'change_leaverequest'),(55,'Can delete leave request',14,'delete_leaverequest'),(56,'Can view leave request',14,'view_leaverequest'),(57,'Can add leave balance',15,'add_leavebalance'),(58,'Can change leave balance',15,'change_leavebalance'),(59,'Can delete leave balance',15,'delete_leavebalance'),(60,'Can view leave balance',15,'view_leavebalance'),(61,'Can add payroll',16,'add_payroll'),(62,'Can change payroll',16,'change_payroll'),(63,'Can delete payroll',16,'delete_payroll'),(64,'Can view payroll',16,'view_payroll'),(65,'Can add salary slip',17,'add_salaryslip'),(66,'Can change salary slip',17,'change_salaryslip'),(67,'Can delete salary slip',17,'delete_salaryslip'),(68,'Can view salary slip',17,'view_salaryslip'),(69,'Can add email log',18,'add_emaillog'),(70,'Can change email log',18,'change_emaillog'),(71,'Can delete email log',18,'delete_emaillog'),(72,'Can view email log',18,'view_emaillog'),(73,'Can add email template',19,'add_emailtemplate'),(74,'Can change email template',19,'change_emailtemplate'),(75,'Can delete email template',19,'delete_emailtemplate'),(76,'Can view email template',19,'view_emailtemplate'),(77,'Can add audit log',20,'add_auditlog'),(78,'Can change audit log',20,'change_auditlog'),(79,'Can delete audit log',20,'delete_auditlog'),(80,'Can view audit log',20,'view_auditlog');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (8,'accounts','user'),(1,'admin','logentry'),(12,'attendance','attendance'),(20,'audit','auditlog'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(9,'employees','department'),(10,'employees','employee'),(11,'employees','employeedocument'),(15,'leaves','leavebalance'),(14,'leaves','leaverequest'),(13,'leaves','leavetype'),(18,'notifications','emaillog'),(19,'notifications','emailtemplate'),(16,'payroll','payroll'),(17,'payroll','salaryslip'),(5,'sessions','session'),(6,'token_blacklist','blacklistedtoken'),(7,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-12 15:19:45.456386'),(2,'contenttypes','0002_remove_content_type_name','2026-10-12 15:19:45.506868'),(3,'auth','0001_initial','2026-10-12 15:19:45.695425'),(4,'auth','0002_alter_permission_name_max_length','2026-10-12 15:19:45.738703'),(5,'auth','0003_alter_user_email_max_length','2026-10-12 15:19:45.743092'),(6,'auth','0004_alter_user_username_opts','2026-10-12 15:19:45.746640'),(7,'auth','0005_alter_user_last_login_null','2026-10-12 15:19:45.750027'),(8,'auth','0006_require_contenttypes_0002','2026-10-12 15:19:45.751751'),(9,'auth','0007_alter_validators_add_error_messages','2026-10-12 15:19:45.758728'),(10,'auth','0008_alter_user_username_max_length','2026-10-12 15:19:45.762719'),(11,'auth','0009_alter_user_last_name_max_length','2026-10-12 15:19:45.767490'),(12,'auth','0010_alter_group_name_max_length','2026-10-12 15:19:45.777894'),(13,'auth','0011_update_proxy_permissions','2026-10-12 15:19:45.783834'),(14,'auth','0012_alter_user_first_name_max_length','2026-10-12 15:19:45.788296'),(15,'accounts','0001_initial','2026-10-12 15:19:46.028679'),(16,'admin','0001_initial','2026-10-12 15:19:46.122385'),(17,'admin','0002_logentry_remove_auto_add','2026-10-12 15:19:46.127579'),(18,'admin','0003_logentry_add_action_flag_choices','2026-10-12 15:19:46.133251'),(19,'employees','0001_initial','2026-10-12 15:19:46.368162'),(20,'attendance','0001_initial','2026-10-12 15:19:46.485416'),(21,'audit','0001_initial','2026-10-12 15:19:46.566823'),(22,'leaves','0001_initial','2026-10-12 15:19:46.877608'),(23,'notifications','0001_initial','2026-10-12 15:19:46.927345'),(24,'payroll','0001_initial','2026-10-12 15:19:47.156128'),(25,'sessions','0001_initial','2026-10-12 15:19:47.183362'),(26,'token_blacklist','0001_initial','2026-10-12 15:19:47.303270'),(27,'token_blacklist','0002_outstandingtoken_jti_hex','2026-10-12 15:19:47.324444'),(28,'token_blacklist','0003_auto_20171017_2007','2026-10-12 15:19:47.340554'),(29,'token_blacklist','0004_auto_20171017_2013','2026-10-12 15:19:47.396142'),(30,'token_blacklist','0005_remove_outstandingtoken_jti','2026-10-12 15:19:47.440891'),(31,'token_blacklist','0006_auto_20171017_2113','2026-10-12 15:19:47.460835'),(32,'token_blacklist','0007_auto_20171017_2214','2026-10-12 15:19:47.603938'),(33,'token_blacklist','0008_migrate_to_bigautofield','2026-10-12 15:19:47.759104'),(34,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-10-12 15:19:47.778547'),(35,'token_blacklist','0011_linearizes_history','2026-10-12 15:19:47.781534'),(36,'token_blacklist','0012_alter_outstandingtoken_user','2026-10-12 15:19:47.792312'),(37,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2026-10-12 15:19:47.806237');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0zwjlc2punzatgukl35j6a1ob0xb1t5h','.eJxVjDsOwyAQRO9CHSHxWT4p0-cMCHYhOIlAMnZl5e6xJRdJNdK8N7OxENelhnXkOUzErsyyy2-XIr5yOwA9Y3t0jr0t85T4ofCTDn7vlN-30_07qHHUfY0AJJIQJpKSvhgpM7oEoNGXPcBRQp1VsVY6mb0qWoLAaLTC5JEM-3wB6ck4EQ:1xGTuo:mf2PgoFQVGMU8qU4I5HhfbF2A8mdc6X7DAVKIC2ln2g','2026-10-27 04:15:02.673126'),('wd92aq7zg1cubkl1u178ihowe0noyx9l','.eJxVjDsOwyAQRO9CHSHxWT4p0-cMCHYhOIlAMnZl5e6xJRdJNdK8N7OxENelhnXkOUzErsyyy2-XIr5yOwA9Y3t0jr0t85T4ofCTDn7vlN-30_07qHHUfY0AJJIQJpKSvhgpM7oEoNGXPcBRQp1VsVY6mb0qWoLAaLTC5JEM-3wB6ck4EQ:1xGHuM:myrzmn9Tw378OFsUkssFA_g3py-GH1-OLwep0MYXmYw','2026-10-26 15:25:46.134788');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees_department`
--

DROP TABLE IF EXISTS `employees_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees_department` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees_department`
--

LOCK TABLES `employees_department` WRITE;
/*!40000 ALTER TABLE `employees_department` DISABLE KEYS */;
INSERT INTO `employees_department` VALUES (1,'Engineering'),(3,'Finance'),(2,'Human Resources');
/*!40000 ALTER TABLE `employees_department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees_employee`
--

DROP TABLE IF EXISTS `employees_employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees_employee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `employee_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `joining_date` date NOT NULL,
  `basic_salary` decimal(10,2) NOT NULL,
  `hra` decimal(10,2) NOT NULL,
  `allowances` decimal(10,2) NOT NULL,
  `pf_percent` decimal(4,2) NOT NULL,
  `tax_deduction` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `department_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_code` (`employee_code`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `employees_employee_department_id_410c23c8_fk_employees` (`department_id`),
  KEY `employees_employee_is_active_bc4a1119` (`is_active`),
  CONSTRAINT `employees_employee_department_id_410c23c8_fk_employees` FOREIGN KEY (`department_id`) REFERENCES `employees_department` (`id`),
  CONSTRAINT `employees_employee_user_id_27bed289_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees_employee`
--

LOCK TABLES `employees_employee` WRITE;
/*!40000 ALTER TABLE `employees_employee` DISABLE KEYS */;
INSERT INTO `employees_employee` VALUES (1,'EMP001','System Administrator','','2025-01-15',90000.00,36000.00,18000.00,12.00,1000.00,1,'2026-10-12 15:19:49.477872',1,1),(2,'EMP002','HR Manager','','2025-01-15',70000.00,28000.00,14000.00,12.00,1000.00,1,'2026-10-12 15:19:49.896940',2,2),(3,'EMP003','Software Engineer','','2025-01-15',50000.00,20000.00,10000.00,12.00,1000.00,1,'2026-10-12 15:19:50.317258',1,3),(4,'EMP004','QA Engineer','','2025-01-15',45000.00,18000.00,9000.00,12.00,1000.00,1,'2026-10-12 15:19:50.738630',1,4),(5,'EMP005','Accountant','','2025-01-15',42000.00,16800.00,8400.00,12.00,1000.00,1,'2026-10-12 15:19:51.167791',3,5),(6,'EMP006','Recruiter','','2025-01-15',40000.00,16000.00,8000.00,12.00,1000.00,1,'2026-10-12 15:19:51.629281',2,6);
/*!40000 ALTER TABLE `employees_employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees_employeedocument`
--

DROP TABLE IF EXISTS `employees_employeedocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees_employeedocument` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `employee_id` bigint NOT NULL,
  `uploaded_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employees_employeedo_employee_id_01ba40e9_fk_employees` (`employee_id`),
  KEY `employees_employeedo_uploaded_by_id_4d5bafb0_fk_accounts_` (`uploaded_by_id`),
  CONSTRAINT `employees_employeedo_employee_id_01ba40e9_fk_employees` FOREIGN KEY (`employee_id`) REFERENCES `employees_employee` (`id`),
  CONSTRAINT `employees_employeedo_uploaded_by_id_4d5bafb0_fk_accounts_` FOREIGN KEY (`uploaded_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees_employeedocument`
--

LOCK TABLES `employees_employeedocument` WRITE;
/*!40000 ALTER TABLE `employees_employeedocument` DISABLE KEYS */;
/*!40000 ALTER TABLE `employees_employeedocument` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leaves_leavebalance`
--

DROP TABLE IF EXISTS `leaves_leavebalance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaves_leavebalance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `year` int unsigned NOT NULL,
  `allocated` decimal(5,1) NOT NULL,
  `used` decimal(5,1) NOT NULL,
  `employee_id` bigint NOT NULL,
  `leave_type_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_balance` (`employee_id`,`leave_type_id`,`year`),
  KEY `leaves_leavebalance_leave_type_id_23644b98_fk_leaves_le` (`leave_type_id`),
  CONSTRAINT `leaves_leavebalance_employee_id_22e425a2_fk_employees` FOREIGN KEY (`employee_id`) REFERENCES `employees_employee` (`id`),
  CONSTRAINT `leaves_leavebalance_leave_type_id_23644b98_fk_leaves_le` FOREIGN KEY (`leave_type_id`) REFERENCES `leaves_leavetype` (`id`),
  CONSTRAINT `leaves_leavebalance_chk_1` CHECK ((`year` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaves_leavebalance`
--

LOCK TABLES `leaves_leavebalance` WRITE;
/*!40000 ALTER TABLE `leaves_leavebalance` DISABLE KEYS */;
INSERT INTO `leaves_leavebalance` VALUES (1,2026,12.0,0.0,1,1),(2,2026,10.0,0.0,1,2),(3,2026,15.0,0.0,1,3),(4,2026,0.0,0.0,1,4),(5,2026,12.0,1.0,3,1),(6,2026,10.0,0.0,3,2),(7,2026,15.0,0.0,3,3),(8,2026,0.0,0.0,3,4),(9,2026,12.0,0.0,2,1),(10,2026,10.0,0.0,2,2),(11,2026,15.0,0.0,2,3),(12,2026,0.0,0.0,2,4);
/*!40000 ALTER TABLE `leaves_leavebalance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leaves_leaverequest`
--

DROP TABLE IF EXISTS `leaves_leaverequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaves_leaverequest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `days` decimal(5,1) NOT NULL,
  `lop_days` decimal(5,1) NOT NULL,
  `reason` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied_at` datetime(6) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `remarks` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_id` bigint NOT NULL,
  `reviewed_by_id` bigint DEFAULT NULL,
  `leave_type_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `leaves_leaverequest_employee_id_b2eba95e_fk_employees` (`employee_id`),
  KEY `leaves_leaverequest_reviewed_by_id_43d77d88_fk_accounts_user_id` (`reviewed_by_id`),
  KEY `leaves_leaverequest_leave_type_id_12a8fd52_fk_leaves_le` (`leave_type_id`),
  KEY `leaves_leaverequest_start_date_abef9d23` (`start_date`),
  KEY `leaves_leaverequest_status_49805770` (`status`),
  CONSTRAINT `leaves_leaverequest_employee_id_b2eba95e_fk_employees` FOREIGN KEY (`employee_id`) REFERENCES `employees_employee` (`id`),
  CONSTRAINT `leaves_leaverequest_leave_type_id_12a8fd52_fk_leaves_le` FOREIGN KEY (`leave_type_id`) REFERENCES `leaves_leavetype` (`id`),
  CONSTRAINT `leaves_leaverequest_reviewed_by_id_43d77d88_fk_accounts_user_id` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaves_leaverequest`
--

LOCK TABLES `leaves_leaverequest` WRITE;
/*!40000 ALTER TABLE `leaves_leaverequest` DISABLE KEYS */;
INSERT INTO `leaves_leaverequest` VALUES (1,'2026-10-14','2026-10-14',1.0,0.0,'personal work','APPROVED','2026-10-14 04:58:01.908165','2026-10-14 04:59:16.353891','done',3,2,1);
/*!40000 ALTER TABLE `leaves_leaverequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leaves_leavetype`
--

DROP TABLE IF EXISTS `leaves_leavetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaves_leavetype` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `annual_quota` decimal(5,1) NOT NULL,
  `is_paid` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaves_leavetype`
--

LOCK TABLES `leaves_leavetype` WRITE;
/*!40000 ALTER TABLE `leaves_leavetype` DISABLE KEYS */;
INSERT INTO `leaves_leavetype` VALUES (1,'Casual Leave',12.0,1),(2,'Sick Leave',10.0,1),(3,'Earned Leave',15.0,1),(4,'Loss of Pay',0.0,0);
/*!40000 ALTER TABLE `leaves_leavetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications_emaillog`
--

DROP TABLE IF EXISTS `notifications_emaillog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications_emaillog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `template_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `to_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `body` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_emaillog_template_code_dcd61023` (`template_code`),
  KEY `notifications_emaillog_created_at_713365a1` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications_emaillog`
--

LOCK TABLES `notifications_emaillog` WRITE;
/*!40000 ALTER TABLE `notifications_emaillog` DISABLE KEYS */;
INSERT INTO `notifications_emaillog` VALUES (1,'PAYROLL_PROCESSED','admin@hrms.local','Payroll processed for September 2026','Hi Admin User,\n\nYour payroll for September 2026 has been processed.\nNet salary: 119,109.09\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.472023'),(2,'SALARY_SLIP_READY','admin@hrms.local','Salary slip for September 2026','Hi Admin User,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.503840'),(3,'PAYROLL_PROCESSED','hr@hrms.local','Payroll processed for September 2026','Hi Helen Roberts,\n\nYour payroll for September 2026 has been processed.\nNet salary: 102,600.00\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.580829'),(4,'SALARY_SLIP_READY','hr@hrms.local','Salary slip for September 2026','Hi Helen Roberts,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.591458'),(5,'PAYROLL_PROCESSED','dinesh@hrms.local','Payroll processed for September 2026','Hi Dinesh Kumar,\n\nYour payroll for September 2026 has been processed.\nNet salary: 65,727.27\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.668928'),(6,'SALARY_SLIP_READY','dinesh@hrms.local','Salary slip for September 2026','Hi Dinesh Kumar,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.679939'),(7,'PAYROLL_PROCESSED','priya@hrms.local','Payroll processed for September 2026','Hi Priya Sharma,\n\nYour payroll for September 2026 has been processed.\nNet salary: 62,327.27\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.750538'),(8,'SALARY_SLIP_READY','priya@hrms.local','Salary slip for September 2026','Hi Priya Sharma,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.761976'),(9,'PAYROLL_PROCESSED','arun@hrms.local','Payroll processed for September 2026','Hi Arun Raj,\n\nYour payroll for September 2026 has been processed.\nNet salary: 55,050.91\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.845497'),(10,'SALARY_SLIP_READY','arun@hrms.local','Salary slip for September 2026','Hi Arun Raj,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.856773'),(11,'PAYROLL_PROCESSED','meena@hrms.local','Payroll processed for September 2026','Hi Meena Iyer,\n\nYour payroll for September 2026 has been processed.\nNet salary: 49,472.73\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.928189'),(12,'SALARY_SLIP_READY','meena@hrms.local','Salary slip for September 2026','Hi Meena Iyer,\n\nYour salary slip for September 2026 is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team','SENT','','2026-10-13 04:51:01.938840'),(13,'LEAVE_APPLIED','dinesh@hrms.local','Leave request submitted (Casual Leave)','Hi Dinesh Kumar,\n\nYour Casual Leave request from Oct. 14, 2026 to Oct. 14, 2026 (1 day(s)) has been submitted and is pending approval.\n\nRegards,\nHR Team','SENT','','2026-10-14 04:58:01.983195'),(14,'LEAVE_APPLIED_HR','admin@hrms.local','New leave request from Dinesh Kumar','Dinesh Kumar applied for Casual Leave from Oct. 14, 2026 to Oct. 14, 2026 (1 day(s)). Please review it in the HRMS.','SENT','','2026-10-14 04:58:01.988326'),(15,'LEAVE_APPLIED_HR','hr@hrms.local','New leave request from Dinesh Kumar','Dinesh Kumar applied for Casual Leave from Oct. 14, 2026 to Oct. 14, 2026 (1 day(s)). Please review it in the HRMS.','SENT','','2026-10-14 04:58:01.990958'),(16,'LEAVE_APPLIED_HR','dineshkumarsenthilk123@gmail.com','New leave request from Dinesh Kumar','Dinesh Kumar applied for Casual Leave from Oct. 14, 2026 to Oct. 14, 2026 (1 day(s)). Please review it in the HRMS.','SENT','','2026-10-14 04:58:01.993357'),(17,'LEAVE_APPROVED','dinesh@hrms.local','Your leave request was approved','Hi Dinesh Kumar,\n\nYour Casual Leave request (Oct. 14, 2026 to Oct. 14, 2026) has been APPROVED.\n\nRegards,\nHR Team','SENT','','2026-10-14 04:59:16.362429');
/*!40000 ALTER TABLE `notifications_emaillog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications_emailtemplate`
--

DROP TABLE IF EXISTS `notifications_emailtemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications_emailtemplate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `body` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications_emailtemplate`
--

LOCK TABLES `notifications_emailtemplate` WRITE;
/*!40000 ALTER TABLE `notifications_emailtemplate` DISABLE KEYS */;
INSERT INTO `notifications_emailtemplate` VALUES (1,'EMPLOYEE_ONBOARDED','Welcome to {{ company }}','Hi {{ name }},\n\nYour HRMS account has been created.\nUsername: {{ username }}\nTemporary password: {{ password }}\n\nPlease log in and change your password.\n\nRegards,\nHR Team'),(2,'LEAVE_APPLIED','Leave request submitted ({{ leave_type }})','Hi {{ name }},\n\nYour {{ leave_type }} request from {{ start }} to {{ end }} ({{ days }} day(s)) has been submitted and is pending approval.\n\nRegards,\nHR Team'),(3,'LEAVE_APPLIED_HR','New leave request from {{ name }}','{{ name }} applied for {{ leave_type }} from {{ start }} to {{ end }} ({{ days }} day(s)). Please review it in the HRMS.'),(4,'LEAVE_APPROVED','Your leave request was approved','Hi {{ name }},\n\nYour {{ leave_type }} request ({{ start }} to {{ end }}) has been APPROVED.{% if lop_days %}\nNote: {{ lop_days }} day(s) will be treated as Loss of Pay.{% endif %}\n\nRegards,\nHR Team'),(5,'LEAVE_REJECTED','Your leave request was rejected','Hi {{ name }},\n\nYour {{ leave_type }} request ({{ start }} to {{ end }}) has been REJECTED.\nRemarks: {{ remarks }}\n\nRegards,\nHR Team'),(6,'PAYROLL_PROCESSED','Payroll processed for {{ period }}','Hi {{ name }},\n\nYour payroll for {{ period }} has been processed.\nNet salary: {{ net }}\n\nRegards,\nPayroll Team'),(7,'SALARY_SLIP_READY','Salary slip for {{ period }}','Hi {{ name }},\n\nYour salary slip for {{ period }} is ready. Log in to the HRMS to download it.\n\nRegards,\nPayroll Team');
/*!40000 ALTER TABLE `notifications_emailtemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payroll_payroll`
--

DROP TABLE IF EXISTS `payroll_payroll`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payroll_payroll` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `year` int unsigned NOT NULL,
  `month` int unsigned NOT NULL,
  `working_days` int unsigned NOT NULL,
  `present_days` decimal(5,1) NOT NULL,
  `paid_leave_days` decimal(5,1) NOT NULL,
  `lop_days` decimal(5,1) NOT NULL,
  `basic` decimal(10,2) NOT NULL,
  `hra` decimal(10,2) NOT NULL,
  `allowances` decimal(10,2) NOT NULL,
  `gross_salary` decimal(10,2) NOT NULL,
  `lop_deduction` decimal(10,2) NOT NULL,
  `pf_deduction` decimal(10,2) NOT NULL,
  `tax_deduction` decimal(10,2) NOT NULL,
  `adjustment` decimal(10,2) NOT NULL,
  `adjustment_note` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `net_salary` decimal(10,2) NOT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `locked` tinyint(1) NOT NULL,
  `generated_at` datetime(6) NOT NULL,
  `credited_at` datetime(6) DEFAULT NULL,
  `transaction_ref` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_id` bigint NOT NULL,
  `generated_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `one_payroll_per_month` (`employee_id`,`year`,`month`),
  KEY `payroll_payroll_generated_by_id_32ea0ab1_fk_accounts_user_id` (`generated_by_id`),
  KEY `payroll_payroll_year_e0c818a0` (`year`),
  KEY `payroll_payroll_month_ef8599ae` (`month`),
  KEY `payroll_payroll_status_45ac8080` (`status`),
  CONSTRAINT `payroll_payroll_employee_id_cd24ccf6_fk_employees_employee_id` FOREIGN KEY (`employee_id`) REFERENCES `employees_employee` (`id`),
  CONSTRAINT `payroll_payroll_generated_by_id_32ea0ab1_fk_accounts_user_id` FOREIGN KEY (`generated_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `payroll_payroll_chk_1` CHECK ((`year` >= 0)),
  CONSTRAINT `payroll_payroll_chk_2` CHECK ((`month` >= 0)),
  CONSTRAINT `payroll_payroll_chk_3` CHECK ((`working_days` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payroll_payroll`
--

LOCK TABLES `payroll_payroll` WRITE;
/*!40000 ALTER TABLE `payroll_payroll` DISABLE KEYS */;
INSERT INTO `payroll_payroll` VALUES (1,2026,9,22,20.0,0.0,2.0,90000.00,36000.00,18000.00,144000.00,13090.91,10800.00,1000.00,0.00,'',119109.09,'GENERATED',1,'2026-10-13 04:51:01.193082',NULL,'',1,1),(2,2026,9,22,22.0,0.0,0.0,70000.00,28000.00,14000.00,112000.00,0.00,8400.00,1000.00,0.00,'',102600.00,'GENERATED',1,'2026-10-13 04:51:01.533628',NULL,'',2,1),(3,2026,9,22,20.0,0.0,2.0,50000.00,20000.00,10000.00,80000.00,7272.73,6000.00,1000.00,0.00,'',65727.27,'GENERATED',1,'2026-10-13 04:51:01.617481',NULL,'',3,1),(4,2026,9,22,21.0,0.0,1.0,45000.00,18000.00,9000.00,72000.00,3272.73,5400.00,1000.00,0.00,'',62327.27,'GENERATED',1,'2026-10-13 04:51:01.703731',NULL,'',4,1),(5,2026,9,22,20.0,0.0,2.0,42000.00,16800.00,8400.00,67200.00,6109.09,5040.00,1000.00,0.00,'',55050.91,'GENERATED',1,'2026-10-13 04:51:01.785529',NULL,'',5,1),(6,2026,9,22,19.0,0.0,3.0,40000.00,16000.00,8000.00,64000.00,8727.27,4800.00,1000.00,0.00,'',49472.73,'GENERATED',1,'2026-10-13 04:51:01.883358',NULL,'',6,1);
/*!40000 ALTER TABLE `payroll_payroll` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payroll_salaryslip`
--

DROP TABLE IF EXISTS `payroll_salaryslip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payroll_salaryslip` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `generated_at` datetime(6) NOT NULL,
  `payroll_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `payroll_id` (`payroll_id`),
  CONSTRAINT `payroll_salaryslip_payroll_id_38b7720a_fk_payroll_payroll_id` FOREIGN KEY (`payroll_id`) REFERENCES `payroll_payroll` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payroll_salaryslip`
--

LOCK TABLES `payroll_salaryslip` WRITE;
/*!40000 ALTER TABLE `payroll_salaryslip` DISABLE KEYS */;
INSERT INTO `payroll_salaryslip` VALUES (1,'slips/EMP001_2026-09_32p9PI8.pdf','2026-10-13 04:51:01.332652',1),(2,'slips/EMP002_2026-09_vEvnl9x.pdf','2026-10-13 04:51:01.567042',2),(3,'slips/EMP003_2026-09_WKWPJq4.pdf','2026-10-13 04:51:01.653489',3),(4,'slips/EMP004_2026-09_9xb5gtF.pdf','2026-10-13 04:51:01.735847',4),(5,'slips/EMP005_2026-09_qZjhAE9.pdf','2026-10-13 04:51:01.821166',5),(6,'slips/EMP006_2026-09_ctYGzdp.pdf','2026-10-13 04:51:01.916238',6);
/*!40000 ALTER TABLE `payroll_salaryslip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
INSERT INTO `token_blacklist_blacklistedtoken` VALUES (1,'2026-10-12 15:30:13.254554',1),(2,'2026-10-13 04:13:13.028641',3),(3,'2026-10-13 04:50:54.248639',4),(4,'2026-10-13 10:06:30.380776',5),(5,'2026-10-13 11:44:11.921128',6),(6,'2026-10-13 12:09:43.087984',2),(7,'2026-10-13 12:12:35.985305',8),(8,'2026-10-13 12:14:45.027869',9),(9,'2026-10-13 12:16:57.012089',7),(10,'2026-10-13 12:17:00.740544',11),(11,'2026-10-13 14:31:30.752873',12),(12,'2026-10-13 15:27:31.634073',13),(13,'2026-10-14 04:28:50.514013',15),(14,'2026-10-14 04:29:41.693410',16),(15,'2026-10-14 04:30:54.644510',17),(16,'2026-10-14 04:32:27.698012',18),(17,'2026-10-14 04:34:39.712318',19),(18,'2026-10-14 04:47:47.892843',20),(19,'2026-10-14 04:49:16.769862',21),(20,'2026-10-14 04:52:18.410226',22),(21,'2026-10-14 04:53:38.021520',23),(22,'2026-10-14 04:56:21.689941',24),(23,'2026-10-14 04:57:07.284657',25),(24,'2026-10-14 04:58:20.538393',26),(25,'2026-10-14 04:59:34.205347',27),(26,'2026-10-14 05:16:50.824961',28);
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `jti` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_accounts_` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
INSERT INTO `token_blacklist_outstandingtoken` VALUES (1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTkwNTM4OCwiaWF0IjoxNzkxODE4OTg4LCJqdGkiOiI5MGQyMmM1YzVkNjQ0MmQyODZkMjEzMDUxYmU3M2JiYyIsInVzZXJfaWQiOiI3In0.xl_hLKzNFR_l3Zfs9P3O0q8s7GlIvY373GCG76YEGBs','2026-10-12 15:29:48.770731','2026-10-13 15:29:48.000000',7,'90d22c5c5d6442d286d213051be73bbc'),(2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTkwNTUyNCwiaWF0IjoxNzkxODE5MTI0LCJqdGkiOiJhNzIyYTM2ZDhjOGQ0ODcxOWJiZTQyMzJlNzA1YmIyNiIsInVzZXJfaWQiOiIxIn0.8Bzl__5x3lOGqmQpci37_-iUpfAFeiwYZ1E2yTkN1QE','2026-10-12 15:32:04.425942','2026-10-13 15:32:04.000000',1,'a722a36d8c8d48719bbe4232e705bb26'),(3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk1MTE3NywiaWF0IjoxNzkxODY0Nzc3LCJqdGkiOiJiNWUxMTY2MjU4ZjY0YmU4OThiMzQ4NDAxNzNjNzdiYSIsInVzZXJfaWQiOiI3In0.yVlodjgnTq3H75MU52Yiv6A6KIRDkc-ox0bekkrXBKE','2026-10-13 04:12:57.293958','2026-10-14 04:12:57.000000',7,'b5e1166258f64be898b34840173c77ba'),(4,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk1MTIwNSwiaWF0IjoxNzkxODY0ODA1LCJqdGkiOiJkOTk0N2YzZmQ1OWY0OTg1OWRjNWIzYWY2NDFiYTZjMCIsInVzZXJfaWQiOiIxIn0.xrC1uWEQdIIZmv1N1xqBkibatf40AEiFR1X12ztT2CE','2026-10-13 04:13:25.234332','2026-10-14 04:13:25.000000',1,'d9947f3fd59f49859dc5b3af641ba6c0'),(5,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk1MzQ1MywiaWF0IjoxNzkxODY3MDUzLCJqdGkiOiIzODVlN2UwOGIyMDQ0MWQwODcxMDA1MzEyODMwMzE1YiIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.NklBhGcOcoy4njernnTMP3hGFRPAsBm-7w5QuPRY1jo','2026-10-13 04:50:53.968782','2026-10-14 04:50:53.000000',1,'385e7e08b20441d0871005312830315b'),(6,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk3MjM5MCwiaWF0IjoxNzkxODg1OTkwLCJqdGkiOiI0OTFhZmEzMWNkY2I0N2ZhYTQ2ZjZlN2NiNDRkYzJmYSIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.1X_Sg9RNY80VgqpmqQBGy9pBgM3c_tIbys7zymDC9Eg','2026-10-13 10:06:30.239399','2026-10-14 10:06:30.000000',1,'491afa31cdcb47faa46f6e7cb44dc2fa'),(7,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk3ODI1MSwiaWF0IjoxNzkxODkxODUxLCJqdGkiOiJlY2Y3NTlkNGEwZmM0OTI0YTdkODMyMzZiNjkxNDYwZiIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.NyMLXC0zsioZPbO1dPfhZc7pDPnsJLF3eRAtz119oo8','2026-10-13 11:44:11.735759','2026-10-14 11:44:11.000000',1,'ecf759d4a0fc4924a7d83236b691460f'),(8,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk3OTc4MywiaWF0IjoxNzkxODkzMzgzLCJqdGkiOiJlNzM1MDhmNmQ0NjM0M2Q4OTIyMWM0MTg4YzYxZWJlNyIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.7atgvmt7FHMHmYZ0JuQxjGOAlRGymaxtKuJ8bWWoHYE','2026-10-13 12:09:43.010120','2026-10-14 12:09:43.000000',1,'e73508f6d46343d89221c4188c61ebe7'),(9,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk3OTk2NiwiaWF0IjoxNzkxODkzNTY2LCJqdGkiOiI0YTEzZTRmZGE3N2E0MzBhODNkYTRlMzJhMGY2ZDQzYyIsInVzZXJfaWQiOiI3In0.AKjYzNtfPXCzAFppFXgE6E8Q7UBh6dkSOiso8UPxiZw','2026-10-13 12:12:46.924064','2026-10-14 12:12:46.000000',7,'4a13e4fda77a430a83da4e32a0f6d43c'),(10,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk4MDEwNCwiaWF0IjoxNzkxODkzNzA0LCJqdGkiOiI5YTJkMjIxNzZiMDk0MjM4YjdlNmZmMThjMWMzYzJiMiIsInVzZXJfaWQiOiI3In0.jAWo_govduk2_P9InWGACAgShh6JfzJ_MLRyqYjBioQ','2026-10-13 12:15:04.341563','2026-10-14 12:15:04.000000',7,'9a2d22176b094238b7e6ff18c1c3c2b2'),(11,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk4MDIxNiwiaWF0IjoxNzkxODkzODE2LCJqdGkiOiJlNzZmNjc1ODI3NzU0N2Q5OTllMTM1ZDhlYzI2ZDJhZCIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.SgpSNwmfxlXNOghP2o0-7dbxTJhoP-ql5uh-zysAhJ4','2026-10-13 12:16:56.935520','2026-10-14 12:16:56.000000',1,'e76f6758277547d999e135d8ec26d2ad'),(12,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk4NDgzNCwiaWF0IjoxNzkxODk4NDM0LCJqdGkiOiJiN2I0ZWYzYWY4YWI0NTFlYWI0OGQ5ZTBmOTA3NTU4MCIsInVzZXJfaWQiOiIxIn0.k8ZE7PK7uywYqzgJlsTFV92eUa4CeUsaiKdspxfYY_E','2026-10-13 13:33:54.794649','2026-10-14 13:33:54.000000',1,'b7b4ef3af8ab451eab48d9e0f9075580'),(13,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk4ODI5MCwiaWF0IjoxNzkxOTAxODkwLCJqdGkiOiJkODU5YjdhMDgzMTQ0NTY2YjkzY2FlMDg4ZGYwMzE2YyIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.yIqtEB7jsf7xvZ4Kc1MGFYIsF8dEVH_zaZ_6DDpBeeo','2026-10-13 14:31:30.603239','2026-10-14 14:31:30.000000',1,'d859b7a083144566b93cae088df0316c'),(14,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTk5MTY1MSwiaWF0IjoxNzkxOTA1MjUxLCJqdGkiOiJmYjc4ZTlkMzNhZmQ0ZDFmYWU0ZDllMzAzNDA1NzllNiIsInVzZXJfaWQiOiIxIiwicm9sZSI6IkFETUlOIiwidXNlcm5hbWUiOiJhZG1pbiJ9.-ENILJrd3HJpQC2csgbToJv0qoaYO7W26ezZhoKRXqM','2026-10-13 15:27:31.235486','2026-10-14 15:27:31.000000',1,'fb78e9d33afd4d1fae4d9e30340579e6'),(15,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzODUyMiwiaWF0IjoxNzkxOTUyMTIyLCJqdGkiOiI1MjZjNmMyNjAyMDM0YjRlOWFhODcxYmIyYmI5ZWJiYiIsInVzZXJfaWQiOiIxIn0.djKcIApgxGelcFk6h1yGXxambyz0QT3lZomQiRwmtiY','2026-10-14 04:28:42.893899','2026-10-15 04:28:42.000000',1,'526c6c2602034b4e9aa871bb2bb9ebbb'),(16,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzODUzNywiaWF0IjoxNzkxOTUyMTM3LCJqdGkiOiI1MWE0NzA1NmM5Mjk0NmE0OWExMWJiYTY5YmZmYWMwNiIsInVzZXJfaWQiOiI3In0.ZwwS7mJrcqmaDsF5vG_8qt3AqCT_l8MmTEimN6HqAi4','2026-10-14 04:28:57.432913','2026-10-15 04:28:57.000000',7,'51a47056c92946a49a11bba69bffac06'),(17,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzODYwNSwiaWF0IjoxNzkxOTUyMjA1LCJqdGkiOiI0ODcxODcyMTk0NzA0YjdiYTFhNjdhMjhhOTBhMjNjOCIsInVzZXJfaWQiOiIxIn0.p0iXldndwDjMGz0wl3fr1ZplmvPwue59SlYtdzNXEwQ','2026-10-14 04:30:05.279194','2026-10-15 04:30:05.000000',1,'4871872194704b7ba1a67a28a90a23c8'),(18,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzODY2MCwiaWF0IjoxNzkxOTUyMjYwLCJqdGkiOiJkZDcyZGJmZGY0ZmU0NGY3OTlmMDZjYWQwYmUzYWQyNyIsInVzZXJfaWQiOiI3In0.AGrrXwGT6BgzknHoNKi5eieSmMknkbaUk1efPuNIChc','2026-10-14 04:31:00.864373','2026-10-15 04:31:00.000000',7,'dd72dbfdf4fe44f799f06cad0be3ad27'),(19,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzODg0MCwiaWF0IjoxNzkxOTUyNDQwLCJqdGkiOiJiMTAxZTg3MjRhNTE0NGU1OTdjYmQxM2U3YWY0MTIwNSIsInVzZXJfaWQiOiI3In0.WZEaqjoiSiQ4sQZAjdZXkzu_3aURHioGqMHu0vOWRGo','2026-10-14 04:34:00.130112','2026-10-15 04:34:00.000000',7,'b101e8724a5144e597cbd13e7af41205'),(20,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzOTAzNiwiaWF0IjoxNzkxOTUyNjM2LCJqdGkiOiJlNTRkNDM5ZGQ4NTE0Zjc1ODM0NTk2NTY4ZWJlNzdjYiIsInVzZXJfaWQiOiIzIn0.23We2J8vZCTp2PbCHnQB1KVGVuK6dqq6DbHejJmwDqw','2026-10-14 04:37:16.823368','2026-10-15 04:37:16.000000',3,'e54d439dd8514f75834596568ebe77cb'),(21,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzOTY4MiwiaWF0IjoxNzkxOTUzMjgyLCJqdGkiOiI1NDRlNjkwMmJkOTk0YWRlYTg1NWE5YWVlODZmYTAyYyIsInVzZXJfaWQiOiI3In0.qmofy-LK8895xosEUdsG42oFZEmWoXn7Hrl_r08ITw0','2026-10-14 04:48:02.494673','2026-10-15 04:48:02.000000',7,'544e6902bd994adea855a9aee86fa02c'),(22,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzOTc4NywiaWF0IjoxNzkxOTUzMzg3LCJqdGkiOiI2MmMzMjZjMTBjNTk0NmM5YjM1MzMwMTdjNDQzZWI3OSIsInVzZXJfaWQiOiI3In0.Yoy7Sfbk8Vu9R6rtosMEyGui0QvsVFAVSWLqu_lE_a0','2026-10-14 04:49:47.820481','2026-10-15 04:49:47.000000',7,'62c326c10c5946c9b3533017c443eb79'),(23,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjAzOTk1MiwiaWF0IjoxNzkxOTUzNTUyLCJqdGkiOiJmNDZhZDA3YjdhZTA0OWYzYmEzMjJiNzAxZDA0YzEzYSIsInVzZXJfaWQiOiIyIn0.-BP0l_hMmGRo76kl13xHj4AbRfwFfkTeIe1PVsr2Ico','2026-10-14 04:52:32.738211','2026-10-15 04:52:32.000000',2,'f46ad07b7ae049f3ba322b701d04c13a'),(24,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MDA0NiwiaWF0IjoxNzkxOTUzNjQ2LCJqdGkiOiI0MjhkNDBhYzcxNDM0NmMzYTE0NmI2YTc3MWUwZTc0ZCIsInVzZXJfaWQiOiIzIn0.1Cehc--llvxB1XMSwnMi533pxQpkmO0id5ZDkWmjz9U','2026-10-14 04:54:06.536996','2026-10-15 04:54:06.000000',3,'428d40ac714346c3a146b6a771e0e74d'),(25,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MDE4OCwiaWF0IjoxNzkxOTUzNzg4LCJqdGkiOiI1M2FiOThiMjkxY2E0YjEwYmU2NjYzOTg5NTc0YmUyOCIsInVzZXJfaWQiOiI3In0.ussOR239yBOGGvQWcZiRBKio9Wt28hmObxYNn0XyOv8','2026-10-14 04:56:28.235803','2026-10-15 04:56:28.000000',7,'53ab98b291ca4b10be6663989574be28'),(26,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MDI1MiwiaWF0IjoxNzkxOTUzODUyLCJqdGkiOiI3ZTg3Mzk2Mjk3Njg0YjY2OTY5YWJjOWQwM2VjMWQ1MyIsInVzZXJfaWQiOiIzIn0.i-JNay3-T5iCgYlpf5WV1NqbTiUEjGvRaaqVpLb9rMU','2026-10-14 04:57:32.111221','2026-10-15 04:57:32.000000',3,'7e87396297684b66969abc9d03ec1d53'),(27,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MDMyNCwiaWF0IjoxNzkxOTUzOTI0LCJqdGkiOiI1NjM0ZjgzNDIwZjk0NTNiYmRiOGY4NjRkMzI1MmExOCIsInVzZXJfaWQiOiIyIn0.v1EKIgMYMxRYOhSSunMxGySgAQOABMlCfEQ42BPdEC8','2026-10-14 04:58:44.893485','2026-10-15 04:58:44.000000',2,'5634f83420f9453bbdb8f864d3252a18'),(28,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MDQxMywiaWF0IjoxNzkxOTU0MDEzLCJqdGkiOiJiOWM3YzU4NTljMGI0MDQyYTM4OTVhMGMwMDE3OThlZSIsInVzZXJfaWQiOiIzIn0.f267zdh3_eTtL4nYDvSOWM62XZBT-TYhJgZWx5DDv1c','2026-10-14 05:00:13.047858','2026-10-15 05:00:13.000000',3,'b9c7c5859c0b4042a3895a0c001798ee'),(29,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjA0MTQxOCwiaWF0IjoxNzkxOTU1MDE4LCJqdGkiOiJjYWU2ZGJkMWI2OTc0YTYzODQxYWVkYzM3NGViMDg1NiIsInVzZXJfaWQiOiI3In0.iXoHhk1FzMuxd-QUNfIeLZrWHEaNQiHLqdcjP5XbDHI','2026-10-14 05:16:58.363132','2026-10-15 05:16:58.000000',7,'cae6dbd1b6974a63841aedc374eb0856');
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-14 10:53:50

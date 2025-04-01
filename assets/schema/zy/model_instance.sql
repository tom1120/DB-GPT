CREATE TABLE dbgpt.model_instance (
	id BIGINT auto_increment NOT NULL,
	host varchar(100) NULL COMMENT '实例ip',
	port INT NULL COMMENT '实例端口',
	model varchar(100) NULL COMMENT '实例名称',
	worker_type varchar(100) NULL COMMENT '实例注册类型',
	params json NULL COMMENT '实例参数',
	gmt_created DATETIME NULL COMMENT '创建时间',
	gmt_modified DATETIME NULL COMMENT '更新时间',
	CONSTRAINT model_instance_pk PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci
COMMENT='模型实例表';

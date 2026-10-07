#!/usr/bin/env python
import click
from flask.cli import FlaskGroup
from knou_shop2.models import ShopMember, Goods
from sqlalchemy import func
from knou_shop2.database import db_session


def create_app():
    from knou_shop2.shop_main import app
    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the Wiki application."""


@cli.command()
def user_create():
    """User Create"""
    admin_user = ShopMember()
    admin_user.name = '관리자'
    admin_user.email = 'admin@knou-mall.kr'
    admin_user.password = '1234'
    admin_user.is_admin = 'Y'
    admin_user.create_date = func.now()

    db_session.add(admin_user)
    db_session.commit()
    
@cli.command()
def goods_insert():
    """Goods Insert"""

    products = (
        ('C 프로그래밍', 15000, 'c-lang.png', 10, 3,
         'C언어에 대한 전반적인 개념과 문법을 익히고, 이를 프로그램 작성에 활용할 수 있는 능력을 기른다.'),
        ('데이터베이스 시스템', 28900, 'database.png', 10, 5,
         '관계형 데이터베이스를 중심으로 데이터베이스 설계, 질의 처리, 트랜잭션 처리, 동시성 제어, 회복 및 인덱스 등의 내용을 학습하며 단순 기술에 대한 이해에서 더 나아가 알고리즘 트레이스, 프레임워크 적용 등 학부 수업에서 진행되지 않은 고급 기술에 대하여 살펴본다.'),
        ('클라우드 컴퓨팅', 28000, 'cloud_computing.jpg', 10, 1,
         '클라우드 컴퓨팅은 서버 가상화, 분산 처리, 서비스 프로비저닝 및 멀티 테넌시 기술 등 클라우드 컴퓨팅에 필요한 이론 및 기술에 대하여 다루고 클라우드 서비스화를 위한 서비스 모델, 배포 모델, 아키텍처 및 보안과 프라이버시에 대하여 학습한다.'),
        ('오픈소스 기반 데이터 분석', 34200, 'opensource.jpg', 10, 2,
         '데이터 분석의 기본 개념부터 실무 활용까지의 전 과정을 오픈소스 도구를 중심으로 학습한다. 학습자는 데이터 수집, 전처리, EDA, 분석, 시각화의 전과정을 습득하며, 이 과정에서 웹 스크래핑와 API를 통한 데이터 수집을 시작으로 텍스트 데이터, 이미지 및 시계열 데이터 등 다양한 유형의 데이터 분석 기법을 실습을 통해 익히게 된다.'),
        ('인공지능', 19400, 'ai_book.jpg', 10, 5,
         '인공지능의 초기 연구로부터 현재의 첨단 기술로 발전하는 과정에서 인공지능의 가능성을 기대할 수 있게 한 의미 있는 이론 및 모델에 대해 소개한다.'),
        ('파이썬', 31500, 'python.jpg', 10, 4,
         '파이썬 프로그래밍 기초는 인공지능 및 빅데이터 분야에서 필수적으로 이용되고 있는 파이썬의 문법적, 기능적 사용법만을 다루는 것에 그치지 않고 정보의 표현 및 컴퓨터의 근본적인 동작 원리를 이해하고 프로그래밍 언어가 가지고 있는 특징을 학습한다.')
    )

    for item in products:
        goods = Goods()
        goods.goods_name = item[0]
        goods.price = item[1]
        goods.goods_photo = item[2]
        goods.goods_cnt = item[3]
        goods.goods_ranking = item[4]
        goods.goods_description = item[5]

        db_session.add(goods)
    
    db_session.commit()


if __name__ == '__main__':
    cli()
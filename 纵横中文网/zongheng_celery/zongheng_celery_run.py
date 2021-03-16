from zongheng_celery.tasks import get_content


class Comment(object):
    def __init__(self, page_num):
        self.page_num = page_num

    def main(self):
        get_content(self.page_num)


if __name__ == '__main__':
    page_num = 2

    comment = Comment(page_num)
    comment.main()

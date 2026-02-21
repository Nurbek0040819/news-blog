from django.contrib.auth import get_user_model
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"
        db_table = 'categories'


class News(models.Model):
    news_title = models.CharField(max_length=255, unique=True)
    news_description = models.CharField(max_length=255)
    news_image = models.ImageField(upload_to='news/')
    news_content = RichTextUploadingField()
    news_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    news_pub_date = models.DateTimeField(auto_now_add=True)
    news_author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    likes = models.ManyToManyField(get_user_model(), related_name='liked_news', blank=True)
    dislikes = models.ManyToManyField(get_user_model(), related_name='disliked_news', blank=True)

    def __str__(self):
        return self.news_title

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    class Meta:
        verbose_name_plural = "News"
        db_table = 'news'


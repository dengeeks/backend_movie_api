from datetime import date
from django.urls import reverse
from django.db import models


# Create your models here.


class Category(models.Model):
    """Категории"""
    name = models.CharField(max_length=150, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Actor(models.Model):
    """Актеры и режиссеры"""
    name = models.CharField(max_length=100, verbose_name='Имя')
    age = models.PositiveSmallIntegerField(default=0, verbose_name='Возраст')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='actors/', verbose_name='Изображение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Актеры и режиссеры'
        verbose_name_plural = 'Актеры и режиссеры'

    def get_absolute_url(self):
        return reverse('actor_detail',kwargs={'slug':self.name})


class Genre(models.Model):
    """Жанры"""
    name = models.CharField(max_length=100, verbose_name='Имя')
    description = models.TextField(verbose_name='Описание')
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Movie(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = (0, 'Черновик')
        PUBLISHED = (1, 'Опубликовано')

    title = models.CharField(max_length=100, verbose_name='Название')
    tagline = models.CharField(max_length=100, default='', verbose_name='Слоган')
    description = models.TextField(verbose_name='Описание')
    poster = models.ImageField(verbose_name='Постер', upload_to='movie/')
    year = models.PositiveSmallIntegerField(verbose_name='Дата выхода', default=2023)
    country = models.CharField(verbose_name='Страна', max_length=30)
    directors = models.ManyToManyField(Actor, verbose_name='Режиссер', related_name='film_director')
    actors = models.ManyToManyField(Actor, verbose_name='Актеры', related_name='film_actor')
    genres = models.ManyToManyField(Genre, verbose_name='Жанры')
    world_premiere = models.DateField(verbose_name='Премьера в мире', default=date.today)
    budget = models.PositiveIntegerField(verbose_name='Бюджет', default=0, help_text="Указывать сумму в долларах!")
    fees_in_usa = models.PositiveIntegerField(
        verbose_name='Сборы в США', default=0, help_text='Указывать сумму в долларах!'
    )
    fees_in_world = models.PositiveIntegerField(
        verbose_name='Сборы в мире', default=0, help_text='Указывать сумму в доллларах'
    )
    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.SET_NULL, null=True
    )
    url = models.SlugField(max_length=130, unique=True)
    draft = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                default=Status.DRAFT, verbose_name='Статус')
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('movie_detail',kwargs={'slug':self.url})

    def get_review(self):
        return self.reviews_set.filter(parent__isnull=True)


    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class MovieShorts(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=100)
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Изображение', upload_to='movie_shorts/')
    movie = models.ForeignKey(Movie, verbose_name='Фильм', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Кадр из фильма'
        verbose_name_plural = 'Кадры из фильма'


class RatingStar(models.Model):
    """Звезды рейтинга фильма"""
    value = models.SmallIntegerField(verbose_name='Значение', default=0)

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'Звезда рейтинга'
        verbose_name_plural = 'Звезды рейтинга'
        ordering = ['-value']


class Rating(models.Model):
    """Рейтинг"""
    ip = models.CharField(max_length=15, verbose_name='IP Адрес')
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='Звезда')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фильм',related_name='ratings')

    def __str__(self):
        return f'{self.star} - {self.movie}'

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'


class Review(models.Model):
    """Отзывы"""
    email = models.EmailField()
    name = models.CharField(verbose_name='Имя', max_length=100)
    text = models.TextField(verbose_name='Сообщение', max_length=5000)
    parent = models.ForeignKey('self', verbose_name='Родитель', on_delete=models.SET_NULL,
                               blank=True, null=True,related_name='children')
    movie = models.ForeignKey(Movie, verbose_name='Фильм', on_delete=models.CASCADE,related_name='reviews')

    def __str__(self):
        return f'{self.name} - {self.movie}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

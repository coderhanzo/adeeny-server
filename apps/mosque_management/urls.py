from django.urls import path, include
from . import views

urlpatterns = [
    path("create-mosque/", views.create_mosque, name="create_mosque"),
    path(
        "get-all-mosques/",
        views.get_all_mosques,
        name="get_all_mosques and liked mosque",
    ),
    # path("update-mosque/", views.GetAndUpdateMosque.as_view(), name="update_mosque"),
    path("get-all-liked-mosques/", views.get_liked_mosques),
    path("create-annoucment/", views.create_announcement, name="create_annoucment"),
    path(
        "get-all-annoucments/", views.get_all_announcements, name="get_all_annoucments"
    ),
    path("delete-mosque/<int:id>/", views.delete_mosque, name="delete_mosque"),
    path('sermons/', views.SermonView.as_view(), name='sermon-create'),
    path('sermons/<int:id>', views.SermonView.as_view(), name='sermon-create'),
    path("get-sermons/", views.get_all_sermons, name="get_sermons"),
    path("delete-sermon/<int:id>/", views.delete_sermon, name="delete_sermon"),
    path('mosques/<int:id>/like/', views.LikeMosqueView.as_view(), name='like-mosque'),
    path('mosques/liked/', views.FavouritedMosquesView.as_view(), name='liked-mosques'),
]

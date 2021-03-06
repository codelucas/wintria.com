from django.db import models

class WintriaUser(models.Model):
    email = models.EmailField(max_length=254, blank=False,
                              null=False, primary_key=True)
    favorite_news = models.CharField(max_length=300, blank=True,
                                     default="No Preference")
    feedback = models.CharField(max_length=2000, blank=True,
                                default="None")

    class Meta:
        db_table = 'WintriaUser_wintriauser'

    def __unicode__(self):
        return self.email[:100]

    def save(self, *args, **kwargs):
        super(WintriaUser, self).save(*args, **kwargs)



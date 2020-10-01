from django.db import models

# Create your models here.

class MakerKey(models.Model):
    STATUS = (
        #Problem needs attention (colored red)
        (-3, 'Kontrollera om ledig'),   #Check if available
        (-2, 'Okänd'),                  #Unknown
        (-1, 'Borttappad'),             #Lost (but not blocked)
        #Should be in the possesion of the key administrator (colored blue)
        (0, 'Ledig'),                   #Available
        #Needs a action (colored yellow)
        (10, 'Ska lämnas in'),          #Needs to be handed out
        (11, 'Ska lämnas ut'),          #Needs to be collected
        #Is not in the possesion of the key administrator but no action requred (colored green)
        (20, 'Utlämnad'),               #Given out to a host
        (21, 'Spärrad')                 #Blocked
    )
    id = models.UUIDField(primary_key=True, editable=False, help_text="The id of the key")
    status = models.IntegerField(default=0, choices=STATUS, help_text="Key status")
    holder = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, help_text="Current key holder")
    pin_code = models.CharField(max_length=300, help_text="Pin code for this key", null=False, blank=False)
    time_limited = models.BooleanField(default=True, help_text="Inidcates that this key has a date when it will stop working")
    check_date = models.DateField(help_text="The last time this key was verified to be in the posession of holder.", db_index=True)
    comment = models.CharField(max_length=1000, help_text="A comment to keep track of any other information.")

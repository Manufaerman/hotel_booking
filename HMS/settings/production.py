from .common import *

os.environ["DJANGO_SETTINGS_MODULE"] = "HMS.settings.production"
DEBUG: False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'Port': 5432,
        'User': 'u90caag0ttelim',
        'Password': 'p3a4e6a563d16cdf7268ceb41bb23533993f2ed91b900f949ece7ed8b0c88c393',
        'Database': 'd71fnk6kip2i3c',
        'URI': 'postgres://u90caag0ttelim:p3a4e6a563d16cdf7268ceb41bb23533993f2ed91b900f949ece7ed8b0c88c393'
               '@cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/',
        'HOST': 'cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com'
    }
}

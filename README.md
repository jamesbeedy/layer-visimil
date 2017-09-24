# Visimil

This charm provides Visimil, an image recognition utility.

# Usage
Visimil makes use of Elasticsearch, so be sure to deploy the elasticsearch charm alongside Visimil.
```bash
juju deploy elasticsearch

juju deploy visimil

juju relate elasticsearch visimil
```

# Authors
* James Beedy <jamesbeedy@gmail.com>

# Copyright
* James Beedy (c) 2017 <jamesbeedy@gmail.com>

# License
* AGPLv3 (see `LICENSE` file)

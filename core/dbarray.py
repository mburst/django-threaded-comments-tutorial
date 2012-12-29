'''Copyright (c) 2011, Ecometrica Canada Limited. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list
of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

- Neither the name of Ecometrica nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.'''

from django.core.exceptions import FieldError, ValidationError
from django.db import models

def require_postgres(connection):
    engine = connection.settings_dict['ENGINE']
    if 'psycopg2' not in engine and 'postgis' not in engine:
        raise FieldError("Array fields are currently implemented only for PostgreSQL/psycopg2")

class ArrayFieldBase(object):
    """Django field type for an array of values. Supported only on PostgreSQL.
    
    This class is not meant to be instantiated directly; instead, field classes
    should inherit from this class and from an appropriate Django model class.
    """
    
    _south_introspects = True
    
    def db_type(self, connection):
        require_postgres(connection)
        return super(ArrayFieldBase, self).db_type(connection=connection) + '[]'
        
    def to_python(self, value):
        # psycopg2 already supports array types, so we don't actually need to serialize
        # or deserialize
        if value is None:
            return None
        if not isinstance(value, (list, tuple)):
            try:
                iter(value)
            except TypeError:
                raise ValidationError("An ArrayField value must be None or an iterable.")
        s = super(ArrayFieldBase, self)
        return [s.to_python(x) for x in value]
            
    def get_prep_value(self, value):
        if value is None:
            return None
        s = super(ArrayFieldBase, self)
        return [s.get_prep_value(v) for v in value]
        
    def run_validators(self, value):
        if value is None:
            super(ArrayFieldBase, self).run_validators(value)
        else:
            for v in value:
                super(ArrayFieldBase, self).run_validators(v)
                
class ArrayFieldMetaclass(models.SubfieldBase):
    pass

def array_field_factory(name, fieldtype, module=ArrayFieldBase.__module__):
    return ArrayFieldMetaclass(name, (ArrayFieldBase, fieldtype),
        {'__module__': module,
        'description': "An array, where each element is of the same type "\
        "as %s." % fieldtype.__name__})
        
# If you want to make an array version of a field not covered below, this is
# the easiest way:
# 
# class FooArrayField(dbarray.ArrayFieldBase, FooField):
#     __metaclass__ = dbarray.ArrayFieldMetaclass
                
IntegerArrayField = array_field_factory('IntegerArrayField', models.IntegerField)
FloatArrayField = array_field_factory('FloatArrayField', models.FloatField)
CharArrayField = array_field_factory('CharArrayField', models.CharField)
TextArrayField = array_field_factory('TextArrayField', models.TextField)

    
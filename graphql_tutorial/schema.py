import graphene
from graphene_django import DjangoObjectType
from app.models import Contact
from graphql_auth.schema import UserQuery
from graphql_auth import mutations

class ContactType(DjangoObjectType):
    # Describe the data that is to be formatted into GraphQL fields
    class Meta:
        model = Contact
        field = ("id", "name", "phone_number")

class Query(graphene.ObjectType):
    #query ContactType to get list of contacts
    list_contact = graphene.List(ContactType)
    read_contact = graphene.Field(ContactType, id=graphene.Int())

    def resolve_list_contact(root, info):
        # We can easily optimize query count in the resolve method
        return Contact.objects.all()
    
    def resolve_read_contact(root, info, id):
        return Contact.objects.get(id=id)

class ContactMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        phone_number = graphene.String()
    contact = graphene.Field(ContactType)
    
    @classmethod
    def mutate(cls, root, info, name, phone_number, id):
        # CREATE #
        contact = Contact(name=name, phone_number=phone_number)
        contact.save()
        
        # UPDATE #
        get_contact = Contact.objects.get(id=id)
        get_contact.name = name
        get_contact.phone_number = phone_number
        get_contact.save()
        return ContactMutation(contact=get_contact)
    
    
class ContactDelete(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    contact = graphene.Field(ContactType)

    @classmethod   
    def mutate(cls, root, info, id):
        contact = Contact(id=id) 
        #########Delete##############
        contact.delete()


class AuthMutation(graphene.ObjectType):
   register = mutations.Register.Field() #predefined settings to register user
   verify_account = mutations.VerifyAccount.Field() #used to verify account
   token_auth = mutations.ObtainJSONWebToken.Field() # get jwt to log in

class Mutation(AuthMutation, graphene.ObjectType):
    create_contact = ContactMutation.Field()
    update_contact = ContactMutation.Field()
    delete_contact = ContactDelete.Field()

    
schema = graphene.Schema(query=Query, mutation=Mutation)

import os

from django.db import connection
from django.test import TestCase

import graphene
from graphene.test import Client

from controls.models import Control
from controls.schema import Query
from core.test_helpers import create_test_interactive_user


class _Context:
  """The field controls are read by a logged-in user only."""
  def __init__(self, user):
    self.user = user

class ModelsTestCase(TestCase):
  DEFAULT_NAME = 'a_field'
  DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
  DEFAULT_USAGE = 'a_form'


  LOCAL_TEST_DATA_NAME = [DEFAULT_NAME]
  FULL_TEST_DATA_NAME = ['Age', 'AntenatalAmountLeft', 'ApprovalOfSMS',
    'BeneficiaryCard', 'Ceiling1', 'Ceiling2', 'CHFID', 'ClaimAdministrator',
    'Confirmation', 'ConfirmationNo', 'ConsultationAmountLeft',
    'ContributionCategory', 'CurrentAddress', 'CurrentDistrict',
    'CurrentMunicipality', 'CurrentVillage', 'Ded1', 'Ded2', 'DeliveryAmountLeft',
    'DistrictOfFSP', 'DOB', 'Education', 'ExpiryDate', 'FamilyType',
    'FirstServicePoint', 'FSP', 'FSPCategory', 'FSPDistrict', 'Gender',
    'GuaranteeNo', 'HFLevel', 'HospitalizationAmountLeft', 'IdentificationNumber',
    'IdentificationType', 'InsureeEmail', 'LastName', 'lblItemCode', 'lblItemCodeL',
    'lblItemLeftL', 'lblItemMinDate', 'lblServiceLeft', 'lblServiceMinDate',
    'MaritalStatus', 'OtherNames', 'PermanentAddress', 'PolicyStatus', 'Poverty',
    'ProductCode', 'Profession', 'RegionOfFSP', 'Relationship',
    'SurgeryAmountLeft', 'TotalAdmissionsLeft', 'TotalAmount', 'TotalAntenatalLeft',
    'TotalConsultationsLeft', 'TotalDelivieriesLeft', 'TotalSurgeriesLeft',
    'TotalVisitsLeft', 'Vulnerability']

  def generate_expected(self, names):
    return {
        'data': {
          'control': {
            'edges': [
              {
                'node': {
                  'name': name
                }
              } for name in names
            ]
          }
        }
      }

  def setUp(self):
    self.query = """
    {
      control{
        edges{
          node{
            name
          }
        }
      }
    }
    """
    self.control_schema = graphene.Schema(query=Query)
    self.maxDiff = None
    self.isolated_tests = "PYTEST_CURRENT_TEST" in os.environ
    self.controls = []
    self.context = _Context(create_test_interactive_user(username='controls_tester'))

  def tearDown(self):
    if isinstance(self.controls, list) and len(self.controls)>0:
      for control in self.controls:
        if control.name:
          control.delete()
        else:
          pass

  # def test_query_without_any_new_control(self):
  #   client = Client(self.control_schema)
  #   executed = client.execute(self.query, context_value=self.context)
  #   self.assertEqual(executed, self.generate_expected([] if self.isolated_tests else self.FULL_TEST_DATA_NAME))

  def test_query_with_one_control(self):


    client = Client(self.control_schema)
    before_executed = client.execute(self.query, context_value=self.context)
    self.controls.append(
      Control.objects.create(
        name=ModelsTestCase.DEFAULT_NAME,
        adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
        usage=ModelsTestCase.DEFAULT_USAGE))
    executed = client.execute(self.query, context_value=self.context)
    self.assertEqual(
      len(before_executed['data']['control']['edges'])+ 1,
      len(executed['data']['control']['edges']) )
    self.tearDown()

  def test_query_with_several_controls(self):
    TEST_DATA_NAMES = []
    client = Client(self.control_schema)
    before_executed = client.execute(self.query, context_value=self.context)
    for nbr in range(1, 4):
      name = f'{ModelsTestCase.DEFAULT_NAME}_{nbr}'
      self.controls.append(
        Control.objects.create(
          name=name,
          adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
          usage=ModelsTestCase.DEFAULT_USAGE))
      TEST_DATA_NAMES.append(name)

    executed = client.execute(self.query, context_value=self.context)
    self.assertEqual(
      len(before_executed['data']['control']['edges'])+ 3,
      len(executed['data']['control']['edges']) )

    self.tearDown()
    


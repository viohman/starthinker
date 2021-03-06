###########################################################################
#
#  Copyright 2019 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

orderContact_Schema = [
  {
    "description": "",
    "name": "contactInfo",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "description": "",
    "name": "contactName",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "description": "",
    "name": "contactTitle",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "description": "PLANNING_ORDER_CONTACT_BUYER_BILLING_CONTACT, PLANNING_ORDER_CONTACT_BUYER_CONTACT, PLANNING_ORDER_CONTACT_SELLER_CONTACT",
    "name": "contactType",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "description": "",
    "name": "signatureUserProfileId",
    "type": "INT64",
    "mode": "NULLABLE"
  }
]

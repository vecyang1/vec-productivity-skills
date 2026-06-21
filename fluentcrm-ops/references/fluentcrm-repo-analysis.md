# FluentCRM Repository Analysis

Use this document as a quick reference for the FluentCRM codebase architecture, file layout, and model APIs.

## Source Repository

- Upstream URL: https://github.com/FluentCRM/fluent-crm
- Analysis date: 2026-06-21

---

## Directory Structure

```
├── app/                  # Main plugin logic
│   ├── Api/              # PHP API Wrappers
│   │   ├── Classes/      # API implementation classes (Contacts, Tags, Lists, etc.)
│   │   └── Api.php       # API manager
│   ├── Functions/        # Global helper functions
│   │   └── helpers.php   # Main FluentCrm() & FluentCrmApi() helpers
│   ├── Hooks/            # Action and filter hooks
│   ├── Http/             # REST Controllers, Middleware, Request handlers
│   ├── Models/           # Eloquent-style ORM Models (Subscriber, Tag, Lists, etc.)
│   └── Services/         # Business logic (Helper, Sanitize, Reporting, etc.)
├── boot/                 # Initialization and bootstrap files
├── config/               # Internal configurations
├── database/             # Migrations and database setup files
├── includes/             # External third-party libraries and helpers
├── resources/            # Frontend resources (JS, CSS)
├── vendor/               # Composer dependencies
└── webpack.mix.js        # Build configuration
```

---

## Key Core Models (`app/Models/`)

FluentCRM utilizes an Eloquent-based ORM model structure (from the Fluent Framework). Below are the primary models:

- **`Subscriber.php`**
  - Represents a contact/subscriber.
  - Table: `fc_subscribers` (prefix-sensitive).
  - Handles contact attributes, tag bindings, list bindings, custom fields, and transition statuses.
- **`Tag.php`**
  - Represents a segmentation tag.
  - Table: `fc_tags`.
- **`Lists.php`**
  - Represents a subscription list.
  - Table: `fc_lists`.
- **`SubscriberPivot.php`**
  - Pivot mapping subscriber relationships (e.g., lists and tags mapping).
  - Table: `fc_subscriber_pivot`.
- **`Company.php`**
  - Represents company profiles.
  - Table: `fc_companies`.
- **`Funnel.php`** & **`FunnelSequence.php`**
  - Automation workflows and sequences.
  - Tables: `fc_funnels`, `fc_funnel_sequences`.
- **`Campaign.php`**
  - Email campaigns and newsletter broadcast data.
  - Table: `fc_campaigns`.

---

## PHP API Wrapper Reference (`app/Api/Classes/`)

Accessible via the global helper: `FluentCrmApi('<key>')`.

### 1. Contacts API (`FluentCrmApi('contacts')`)
Mapped to `FluentCrm\App\Api\Classes\Contacts`.

- **`getContact($idOrEmail)`**
  - Retrieves a subscriber model by numeric ID or email string.
  - Returns `false` or `Subscriber` model instance.
- **`getContactByUserRef($userIdOrEmail)`**
  - Retrieves a subscriber matching WP user ID or email.
- **`getContactByUserId($userId)`**
  - Retrieves a subscriber by WP user ID.
- **`createOrUpdate($data, $forceUpdate = false, $deleteOtherValues = false, $sync = false)`**
  - Main upsert method. Automatically maps custom fields and updates contact record.
- **`getCurrentContact($cached = true, $useSecureCookie = false)`**
  - Retrieves the contact object of the currently logged-in WordPress user.
- **`query($args)`**
  - Returns a `ContactsQuery` instance for complex filtering.
- **`getCustomFields($types = [], $byOptions = false)`**
  - Retrieves custom contact fields.
- **`getInstance()`**
  - Returns the raw, un-wrapped `Subscriber` model instance.

### 2. Tags API (`FluentCrmApi('tags')`)
Mapped to `FluentCrm\App\Api\Classes\Tags`.

- **`importBulk($tags)`**
  - Imports/saves a list of tags in bulk. Triggers WP actions `fluent_crm/tag_created` or `fluent_crm/tag_updated`.
- **`getInstance()`**
  - Returns the underlying `Tag` model instance.

### 3. Lists API (`FluentCrmApi('lists')`)
Mapped to `FluentCrm\App\Api\Classes\Lists`.

- **`importBulk($lists)`**
  - Imports/saves lists in bulk. Triggers WP actions `fluent_crm/list_created` or `fluent_crm/list_updated`.
- **`getInstance()`**
  - Returns the underlying `Lists` model instance.

---

## Global Helpers (`app/Functions/helpers.php`)

- **`FluentCrm($module = null)`**: Core bootstrapper and module container.
- **`FluentCrmApi($key = null)`**: API wrapper provider.
- **`fluentcrm_get_meta($objectId, $objectType, $key)`**: Meta value retriever.
- **`fluentcrm_update_meta($objectId, $objectType, $key, $value)`**: Meta updater.
- **`fluentCrmTimestamp()`**: Current timezone-adjusted timestamp.

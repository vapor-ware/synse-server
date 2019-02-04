# Tags
## Summary
Synse v3 changes how devices are modeled and referenced for targeted actions. Instead of
ascribing mandatory locational information in the form of a `rack/board/device` hierarchy,
Synse v3 will route to devices based on arbitrary **tags** associated with that device.

This change will make Synse more flexible in how it can route to devices. It also allows
for a more natural method of grouping devices, particularly those that do not live on a
rack or board (e.g. room-level sensors). 

## High Level Work Items
- Update Synse Server's routing and caching logic to replace `rack/board/device` routing
  with the new tag-based routing system.
- Update Synse Server's HTTP API, in accordance with the [API spec](api.md), to use the
  tag-based routing system.
- Update internal models and schemes to conform to the API and device modeling changes.
- Update the GRPC API to replace `rack/board/device` routing with tag-based routing.
- Update the GRPC API to support the new group operations that are supported by the
  tag-based routing system.
- Update device modeling in the SDK to replace `rack/board/device` information with
  tag information.
- Add logic to auto-generate tags based on config values.

## Proposal
### Definitions
The following definitions provide the specific meaning of key terms found within this document.

| Term | Definition |
| ---- | ---------- |
| *tag* | A single string that acts as a group identifier to which an associated Synse device belongs. |
| *label* | A component of the *tag*. The label corresponds to the group name. |
| *annotation* | An optional prefix to the *label* component of the tag. It provides context for the label. |
| *namespace* | An optional prefix to the *annotation*/*label* component(s) of the tag. It serves to provide tag scoping. |
| *tag components* | The collection of *label*, *annotation*, and *namespace*. |

### Tag Anatomy
```

 [NAMESPACE/][ANNOTATION:]LABEL

```

The scheme above shows all components which make up a tag. Components in brackets are optional. 
Below, each component is described in more detail.

#### Label
The label is the only required component of the tag. A tag may consist of only a label. The label
is just a name which is used to identify a group which devices may be a member of. A label group
can have 1..N members.

> **Exception**: The *only* label group which will not have 1..N members is the reserved `id`
tag. This tag will have exactly 1 member.

#### Annotation
The annotation is an optional prefix to the *label* component. It is separated from the
label with a colon (`:`). Annotations can be used to provide additional context and scoping
to a label. [Auto-generated tags](#auto-generated) will always use annotations; the
annotation values for auto-generated tags are reserved and will result in an SDK error
if a user tries to use them.

A tag may have only one annotation.

##### Reserved Annotations
Auto-generated tags reserve the following annotations:
- `id:`
- `type:`

#### Namespace
The namespace is an optional prefix to a *label* or *annotation* component. It is separated
from the annotation or label with a forward slash (`/`). Namespaces allow the formation of 
different tag profiles, where there might otherwise be overlap with tag names. It is important
to note that the namespace applies only to the tag it is a component of; it does not apply
to the device itself (e.g. a single device can have multiple tags in different namespaces).

> **Note**: The use case for tag namespaces will likely be narrow for the initial v3 release. 
Looking forward, it enables tighter control around user access to devices and device actions.

A tag without an explicit namespace defined will be put into the `default` namespace.
The default namespace may be applied explicitly, e.g. `default/foo`. The "default" namespace
is reserved.

A tag may have only one namespace.

##### System-wide Namespace
Some tags may need to apply to all namespaces, such as the auto-generated `id` tag. For
such cases, the *system-wide namespace* should be used. This namespace, identified with 
`system/`, considers the tag a member of all namespaces. It is strongly discouraged
to put custom tags into the system-wide namespace.

#### Tag
A tag is the combination of all components described above. It is a single string with
the (optional) *namespace*, (optional) *annotation*, and (required) *label* components.

Tags are used to reference devices in Synse, replacing the `rack/board/device` identifier in
Synse v1-v2. Synse Server commands which deal with device resources (e.g. `/read`, `/write`)
will support a `tags` query parameter. If multiple tags are specified, they should be comma
separated (see the [API Spec](api.md) for more information).

Any Synse Server command which supports a `tags` query parameter will also support a `ns` (namespace)
query parameter. This can be used to set the namespace for the tags in the query. The namespace 
provided by the query param is only applied if that tag does not already have a namespace.

### Tag Types
#### Auto Generated
Auto-generated tags are tags which are associated with a device automatically, without
any need for user configuration. These tags are currently limited to `id` and `type`.

All auto-generated tags will include an annotation component. The annotation will be [well-known
and reserved](#reserved-annotations) from use in [user-defined tags](#user-defined). If a user-defined
tag annotation conflicts with a reserved annotation name, an error will be raised, causing the
plugin to terminate.

#### User Defined
User-defined tags may be specified for a device in the device's config itself. For example
(using pseudo-config):

```yaml
device:
  type: temperature
  labels:
  - vaporio/fan-sensor
```

If any component of a user-defined tag conflicts with a reserved name, an error will be raised
by the plugin, causing it to terminate.

### Formatting
Below are the rules for tag formatting:

- Tags must be strings
- Tags are case-insensitive (prefer all lower cased)
- Tag components may NOT contain any of the delimiter characters (`:`, `/`, `,`)
- Tags may not contain spaces

### Examples

0. **A tag consisting of only a label**
   ```
   temperature
   ```
0. **A tag consisting of an annotation and a label**
   ```
   type:temperature
   ```
0. **A tag consisting of a namespace and a label**
   ```
   vaporio/temperature
   ```
0. **A tag consisting of a namespace, annotation, and a label**
   ```
   vaporio/type:temperature
   ```
0. **Explicitly setting a tag to the default namespace**
   ```
   default/temperature
   ```
0. **Passing a single tag to Synse Server**
   ```
   ?tags=vaporio/type:temperature
   ```
   The above translates to the following tag(s):
   ```
   vaporio/type:temperature
   ```
0. **Passing multiple tags to Synse Server**
   ```
   ?tags=vaporio/type:temperature,foo,other/bar
   ```
   The above translates to the following tag(s):
   ```
   vaporio/type:temperature
   default/foo
   other/bar
   ```
0. **Setting a namespace and specifying a tag to Synse Server**
   ```
   ?ns=vaporio&tags=type:temperature
   ```
   The above translates to the following tag(s):
   ```
   vaporio/type:temperature
   ```
0. **Setting a namespace and specifying some namespaced tags to Synse Server**
   ```
   ?ns=vaporio&tags=vaporio/type:temperature,foo,other/bar
   ```
   The above translates to the following tag(s):
   ```
   vaporio/type:temperature
   vaporio/foo
   other/bar
   ```  

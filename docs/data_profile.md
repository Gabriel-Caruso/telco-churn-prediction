# SPA:
# Perfil de datos — Telco Customer Churn

Dataset: IBM Telco Customer Churn (7043 clientes, 21 variables).  
Análisis realizado en `notebooks/02_exploration`.  

## Hallazgos sobre el negocio

### El punto de partida

**Sobre el dataset:** IBM Telco Customer Churn. Una fila por cliente de una empresa de telecomunicaciones. La variable objetivo indica si el cliente se dio de baja durante el último mes.

**El problema de negocio:** aumentar la retención de clientes a partir del estudio de los datos y construir un modelo que identifique a los clientes con mayor riesgo de darse de baja.

### Cuántos clientes se van

**Tasa global de baja: 26,54 %.**

Conviene leer bien ese número. No es una previsión, sino una descripción de lo que ha sucedido en la empresa: de los 7043 clientes registrados, 1869 se dieron de baja. Dar con los motivos que hay detrás y atajarlos es el objetivo de todo este análisis.

### Cuándo se van

Al desglosar esa tasa por antigüedad aparece un patrón muy marcado:

| Antigüedad | Tasa de baja |
|---|---|
| 1 mes | 62,0 % |
| 2 meses | 51,7 % |
| 3 meses | 47,0 % |
| 4 meses | 47,2 % |
| 70 meses | 9,2 % |
| 72 meses | 1,7 % |

El problema de retención está, principalmente, en los primeros meses. Quien supera los dos años apenas se marcha.

### Qué producto tienen

Para entender qué provoca las bajas hay que mirar los servicios contratados. Ahí aparece algo contraintuitivo: los clientes que pagan las tarifas más reducidas **parecen ser los más fieles**.

| Servicio | Clientes | Tasa de baja |
|---|---|---|
| Fibra óptica | 3096 | 41,9 % |
| DSL | 2421 | 19,0 % |
| Sin internet | 1526 | 7,4 % |

La tasa de bajas se dispara entre quienes contrataron fibra óptica. ¿Significa eso que el problema está en la fibra? A primera vista podría parecerlo, pero nunca hay que fiarse de los datos en bruto sin cruzarlos contra el resto de variables. Al aislar únicamente a los clientes de fibra y desglosarlos por cantidad de servicios contratados, encontramos lo siguiente:

| Servicios contratados | Tasa de baja |
|---|---|
| 0 | 60 % |
| 1 | 55 % |
| 2 | 48 % |
| 3 | 38 % |
| 4 | 32 % |
| 5 | 19 % |
| 6 | 9 % |

Los clientes que contratan más servicios tienen una tasa de baja mucho menor. **El problema está en la fibra contratada sola.**

### Tipo de contrato

Esto nos lleva al estudio de las variables contractuales, donde encontramos que:

| Tipo de contrato | Tasa de baja |
| --- | --- |
| Mes a mes | 43 % |
| Un año | 11 % |
| Dos años | 3 % |

Puede resultar obvio, ya que los clientes con permanencia son los que más se retienen por la propia naturaleza del contrato. Sabiendo esto, el resto de variables —método de pago, cómo recibe la factura, etc.— pueden estar muy relacionadas con el tipo de contrato y hay que mirarlas con sumo cuidado.

### Forma de pago

Al mirar cómo paga el cliente, el cheque electrónico destaca de forma alarmante:

| Forma de pago | Tasa de baja |
| --- | --- |
| Cheque electrónico | 45 % |
| Cheque por correo | 19 % |
| Transferencia automática | 17 % |
| Tarjeta automática | 15 % |

La lectura inmediata sería "el cheque electrónico provoca bajas". Pero antes de llevar eso a una reunión conviene comprobar algo: **el 78 % de quienes pagan con cheque electrónico tiene contrato mes a mes**, frente al 55 % del conjunto de la empresa.

Es decir, ese grupo no solo paga distinto, sino que además está lleno de clientes sin permanencia, que ya sabíamos que se van más. Parte de ese 45 % no es del cheque, es del contrato que lleva pegado.

Para saber cuánto, hay que comparar clientes **con el mismo tipo de contrato**. Y ahí el resultado es claro: entre los clientes de mes a mes, quienes pagan con cheque electrónico se dan de baja el 53 %, mientras que las otras tres formas de pago se quedan entre el 31 % y el 34 %.

**Conclusión:** el contrato explicaba una parte, pero no todo. A igualdad de contrato, el cheque electrónico sigue asociado a unos 20 puntos más de bajas. Domiciliar el pago, en cambio, se asocia a permanencia incluso entre los clientes sin compromiso.

### No todos los servicios retienen igual

Habíamos visto que contratar más servicios se asocia a menos bajas. Pero al mirar servicio por servicio aparecen dos grupos muy distintos:

| Servicio | Diferencia entre tenerlo y no tenerlo |
| --- | --- |
| Seguridad online | ~27 puntos |
| Soporte técnico | ~26 puntos |
| Copia de seguridad | ~19 puntos |
| Protección de dispositivos | ~17 puntos |
| Películas en streaming | ~4 puntos |
| Televisión en streaming | ~3 puntos |

Los servicios que **resuelven problemas** acompañan a la permanencia. Los de **entretenimiento** no la mueven prácticamente nada.

Esto convierte un hallazgo general en una recomendación concreta: si la empresa quiere retener a un cliente de fibra sin extras ofreciéndole un complemento, los datos apuntan a soporte técnico o seguridad, no a streaming.

### Perfil del cliente

| Variable | Tasa de baja |
| --- | --- |
| 65 años o más | 42 % |
| Menor de 65 | 24 % |
| Sin pareja | 33 % |
| Con pareja | 20 % |
| Sin personas a cargo | 31 % |
| Con personas a cargo | 16 % |

El cliente que vive solo, sin pareja ni personas a cargo, y el cliente mayor, se dan de baja bastante por encima de la media.

En cambio **el sexo del cliente no influye**: hombres y mujeres se dan de baja prácticamente al mismo ritmo, en torno al 26 %. No hay ahí ninguna señal que un modelo pueda aprender.

### Lo que estos datos no pueden responder

Hay que tener en cuenta una serie de cosas importantes:

**No sabemos por qué la fibra falla.** Los datos dicen que los clientes de fibra se van mucho más, pero no si es por precio, por calidad del servicio o porque la competencia ataca justo a ese segmento. Esa información no está en el sistema.

**No sabemos si los servicios retienen o solo lo parecen.** Puede que contratar soporte técnico haga más incómodo cambiarse de compañía, o puede que el cliente que ya pensaba quedarse sea el que va sumando extras. Las dos explicaciones encajan igual de bien con los datos y llevan a decisiones opuestas: en el primer caso, regalar servicios reduce la fuga; en el segundo, solo cuesta dinero.

**Lo mismo vale para el contrato largo.** No sabemos si ata al cliente o si lo elige quien ya tenía intención de quedarse. Posiblemente sea lo primero, pero no podemos arriesgarnos a dar un veredicto así.

Las tres se resolverían igual: con una campaña controlada, ofreciendo el complemento a un grupo de clientes elegidos al azar y comparando su comportamiento con el de un grupo equivalente que no lo recibe.

### Dónde actuar, en orden

1. **Los tres primeros meses.** Más de la mitad de los clientes nuevos se marcha antes del trimestre y de ahí sale casi un tercio de todas las bajas.
2. **La fibra contratada sola.** Es el grupo más numeroso y el más caro de perder.
3. **Los clientes sin domiciliación bancaria.** Se van más incluso comparados con clientes de su mismo tipo de contrato.

# -----------------------------------------------------
# -----------------------------------------------------

# ENG:

## Business findings

### Starting point

**About the dataset:** IBM Telco Customer Churn. One row per customer of a telecommunications company. The target variable indicates whether the customer left during the last month.

**The business problem:** to improve customer retention through data analysis and to build a model that identifies the customers at greatest risk of leaving.

### How many customers leave

**Overall churn rate: 26.54%.**

That figure is worth reading carefully. It is not a forecast but a description of what has already happened at the company: of the 7,043 registered customers, 1,869 left. Finding the reasons behind that and addressing them is the goal of this whole analysis.

### When they leave

Breaking that rate down by tenure reveals a very sharp pattern:

| Tenure | Churn rate |
|---|---|
| 1 month | 62.0% |
| 2 months | 51.7% |
| 3 months | 47.0% |
| 4 months | 47.2% |
| 70 months | 9.2% |
| 72 months | 1.7% |

The retention problem lies mainly in the first few months. Customers who make it past two years barely leave at all.

### What product they hold

To understand what drives churn we need to look at the services customers hold. Something counter-intuitive emerges there: the customers paying the lowest fees **appear to be the most loyal**.

| Service | Customers | Churn rate |
|---|---|---|
| Fiber optic | 3,096 | 41.9% |
| DSL | 2,421 | 19.0% |
| No internet | 1,526 | 7.4% |

Churn spikes among customers who took fiber optic. Does that mean fiber is the problem? At first glance it might look that way, but raw figures should never be trusted without cross-checking them against the other variables. Isolating fiber customers only and breaking them down by number of contracted services, we find the following:

| Services held | Churn rate |
|---|---|
| 0 | 60% |
| 1 | 55% |
| 2 | 48% |
| 3 | 38% |
| 4 | 32% |
| 5 | 19% |
| 6 | 9% |

Customers holding more services churn far less. **The problem is fiber bought on its own.**

### Contract type

This leads us to the contractual variables, where we find:

| Contract type | Churn rate |
| --- | --- |
| Month-to-month | 43% |
| One year | 11% |
| Two years | 3% |

This may seem obvious, since customers under commitment are the ones most likely to stay by the very nature of the contract. Knowing this, the remaining variables — payment method, how the invoice is received, and so on — may be closely tied to contract type and must be examined with great care.

### Payment method

Looking at how customers pay, electronic check stands out alarmingly:

| Payment method | Churn rate |
| --- | --- |
| Electronic check | 45% |
| Mailed check | 19% |
| Bank transfer (automatic) | 17% |
| Credit card (automatic) | 15% |

The immediate reading would be "electronic check causes churn". But before taking that into a meeting, one thing is worth checking: **78% of those paying by electronic check are on month-to-month contracts**, against 55% across the company.

In other words, that group does not merely pay differently: it is also full of customers with no commitment, who we already knew leave more often. Part of that 45% is not down to the payment method but to the contract it drags along.

To find out how much, we need to compare customers **on the same type of contract**. The result there is clear: among month-to-month customers, those paying by electronic check churn at 53%, while the other three payment methods sit between 31% and 34%.

**Conclusion:** contract explained part of it, but not all. With contract held constant, electronic check is still associated with some 20 additional points of churn. Setting up automatic payment, by contrast, is associated with staying, even among customers with no commitment.

### Not all services retain equally

We had seen that holding more services is associated with less churn. But looking service by service, two very different groups emerge:

| Service | Gap between holding it and not |
| --- | --- |
| Online security | ~27 points |
| Tech support | ~26 points |
| Online backup | ~19 points |
| Device protection | ~17 points |
| Streaming movies | ~4 points |
| Streaming TV | ~3 points |

Services that **solve problems** go hand in hand with retention. **Entertainment** ones barely move it at all.

This turns a general finding into a concrete recommendation: if the company wants to retain a fiber customer with no add-ons by offering them a service, the data points to tech support or security rather than streaming.

### Customer profile

| Variable | Churn rate |
| --- | --- |
| 65 or older | 42% |
| Under 65 | 24% |
| No partner | 33% |
| With partner | 20% |
| No dependents | 31% |
| With dependents | 16% |

Customers living alone, without a partner or dependents, and older customers, churn well above the average.

By contrast, **the customer's sex has no influence**: men and women churn at practically the same rate, around 26%. There is no signal there for a model to learn.

### What this data cannot answer

Several important points must be kept in mind:

**We do not know why fiber is failing.** The data says fiber customers leave far more often, but not whether it is down to price, service quality, or competitors targeting that segment specifically. That information is not in the system.

**We do not know whether services retain customers or merely appear to.** Holding tech support may make switching provider more of a hassle, or the customer who already intended to stay may simply be the one who keeps adding extras. Both explanations fit the data equally well and lead to opposite decisions: in the first case, giving services away reduces churn; in the second, it only costs money.

**The same applies to long contracts.** We do not know whether they tie the customer in or whether they are chosen by those who already meant to stay. It is probably the former, but we cannot risk issuing a verdict on that.

All three would be settled the same way: through a controlled campaign, offering the add-on to a randomly selected group of customers and comparing their behaviour against an equivalent group that does not receive it.

### Where to act, in order

1. **The first three months.** More than half of new customers leave before completing the quarter, and almost a third of all churn comes from there.
2. **Fiber bought on its own.** It is the largest group and the most expensive to lose.
3. **Customers without automatic payment.** They leave more even when compared against customers on the same type of contract.



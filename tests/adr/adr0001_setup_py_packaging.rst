Packaging of controller_ironcar_octonomous
##########################################

``setuptools`` is used as packaged builder. The definition is
done through the file ``setup.py``.

.. literalinclude:: ../../setup.py

source distribution
*******************

* Requirement 1 : controller_ironcar code is embedded in the source distribution
* Requirement 2 : default autopilot is available in the source distribution

As user, I can setup the application with the command :

.. code-block::

    pip install git+https://github.com/ironcarocto/controller_ironcar_octonomous.git@master